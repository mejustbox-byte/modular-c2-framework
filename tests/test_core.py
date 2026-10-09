import json
import unittest
from unittest.mock import patch

from mocklab import Lab, LabError


def payload(op="ping", **updates):
    data = dict(
        schema_version=1,
        request_id="req-1",
        lab_id="lab-1",
        agent_id="mock-1",
        operation=op,
        issued_at=100,
    )
    data.update(updates)
    return json.dumps(data).encode()


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.lab = Lab(
            "lab-1",
            {"viewer": "viewer", "operator": "operator", "admin": "lab-admin"},
            clock=lambda: 100,
        )

    def test_lifecycle(self):
        self.assertEqual(self.lab.execute("operator", payload()), {"reply": "pong"})
        self.assertEqual(
            self.lab.execute(
                "operator",
                payload("emit_test_event", request_id="req-2", fixture_id="synthetic-login"),
            )["event"],
            "mock_login",
        )
        self.lab.execute("admin", payload("stop", request_id="req-3"))
        self.assertEqual(
            self.lab.execute("viewer", payload("status", request_id="req-4")), {"state": "stopped"}
        )
        with self.assertRaisesRegex(LabError, "agent_stopped"):
            self.lab.execute("operator", payload(request_id="req-5"))

    def test_denied_roles_and_scope(self):
        for actor, data in [
            ("viewer", payload("stop")),
            ("unknown", payload()),
            ("admin", payload(lab_id="other")),
            ("operator", payload(agent_id="other")),
        ]:
            with self.subTest(actor=actor, data=data), self.assertRaises(LabError):
                self.lab.execute(actor, data)
        self.assertTrue(all(e["outcome"] == "denied" for e in self.lab.audit("viewer")))

    def test_strict_schema(self):
        cases = [
            payload(role="lab-admin"),
            payload("shell"),
            payload(schema_version=True),
            payload(issued_at=float("nan")),
            payload(request_id="/etc/passwd"),
            payload(fixture_id=None),
            payload("emit_test_event", fixture_id="https://test"),
            b"{}",
            b"[]",
            b"\xff",
            b'{"a":1,"a":2}',
            b"x" * 4097,
            payload(operation=[]),
            payload(issued_at=True),
            payload(issued_at=10**400),
        ]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(LabError):
                self.lab.execute("operator", data)
        self.assertNotIn("/etc/passwd", str(self.lab.audit("viewer")))

    def test_expiry_and_future(self):
        for issued_at in [39, 101]:
            with self.subTest(issued_at=issued_at), self.assertRaisesRegex(LabError, "expired"):
                self.lab.execute("operator", payload(issued_at=issued_at))

    def test_replay(self):
        self.lab.execute("operator", payload("stop"))
        with self.assertRaisesRegex(LabError, "replay"):
            self.lab.execute("admin", payload("stop"))
        self.assertEqual(len(self.lab.audit("viewer")), 3)

    def test_audit_capacity_prevents_effect(self):
        lab = Lab("lab-1", {"op": "operator"}, max_events=3, clock=lambda: 100)
        lab.execute("op", payload())
        with self.assertRaisesRegex(LabError, "audit_full"):
            lab.execute("op", payload("stop", request_id="req-2"))
        self.assertFalse(lab._stopped)

    def test_terminal_audit_failure_latches(self):
        original = self.lab._audit

        def failing(actor, request, outcome, reason):
            if outcome == "completed":
                raise OSError("synthetic failure")
            original(actor, request, outcome, reason)

        with patch.object(self.lab, "_audit", side_effect=failing):
            with self.assertRaisesRegex(LabError, "audit_failed"):
                self.lab.execute("operator", payload("stop"))
        with self.assertRaisesRegex(LabError, "audit_blocked"):
            self.lab.execute("operator", payload("status", request_id="req-2"))

    def test_authorization_audit_failure_prevents_effect(self):
        with patch.object(self.lab, "_audit", side_effect=OSError):
            with self.assertRaises(OSError):
                self.lab.execute("operator", payload("stop"))
        self.assertFalse(self.lab._stopped)

    def test_no_network_or_process_operations(self):
        with (
            patch("socket.socket", side_effect=AssertionError("socket")),
            patch("subprocess.Popen", side_effect=AssertionError("process")),
            patch("builtins.open", side_effect=AssertionError("file")),
        ):
            self.lab.execute("operator", payload())
            self.lab.execute("operator", payload("stop", request_id="req-2"))

    def test_audit_copy_and_access(self):
        self.lab.execute("operator", payload())
        events = self.lab.audit("viewer")
        events[0]["outcome"] = "tampered"
        self.assertEqual(self.lab.audit("viewer")[0]["outcome"], "allowed")
        with self.assertRaisesRegex(LabError, "unauthorized"):
            self.lab.audit("unknown")

    def test_configuration(self):
        for kwargs in [dict(max_events=True), dict(max_requests=10001)]:
            with self.assertRaises(LabError):
                Lab("lab-1", {}, **kwargs)
        with self.assertRaises(LabError):
            Lab("lab-1", {"actor": "root"})

    def test_request_capacity(self):
        lab = Lab("lab-1", {"op": "operator"}, max_requests=2, clock=lambda: 100)
        for request_id in ["one", "two"]:
            lab.execute("op", payload(request_id=request_id))
        with self.assertRaisesRegex(LabError, "request_capacity"):
            lab.execute("op", payload("stop", request_id="three"))
        self.assertFalse(lab._stopped)


if __name__ == "__main__":
    unittest.main()
