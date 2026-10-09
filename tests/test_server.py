import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch

from test_core import payload

from mocklab import Lab, LabError
from mocklab.containment import verify
from mocklab.server import Application, object_json
from mocklab.storage import Journal


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.lab = Lab(
            "lab-1", {"admin": "lab-admin", "viewer": "viewer", "op": "operator"}, clock=lambda: 100
        )
        principals = {
            hashlib.sha256(actor.encode()).hexdigest(): actor for actor in ["admin", "viewer", "op"]
        }
        self.app = Application(self.lab, principals, clock=lambda: 100)

    def test_auth_and_expiry(self):
        self.assertEqual(self.app.actor(b"op"), "op")
        with self.assertRaises(LabError):
            self.app.actor(b"unknown")
        self.app.clock = lambda: 701
        with self.assertRaises(LabError):
            self.app.actor(b"op")

    def test_membership_rbac_revoke_and_regrant(self):
        data = dict(
            target="viewer", role="operator", request_id="one", issued_at=100, lab_id="lab-1"
        )
        with self.assertRaisesRegex(LabError, "unauthorized"):
            self.app.dispatch("op", "/api/members", json.dumps(data).encode())
        self.app.dispatch("admin", "/api/members", json.dumps(data).encode())
        self.assertEqual(self.app.dispatch("viewer", "/api/execute", payload()), {"reply": "pong"})
        data.update(role=None, request_id="two")
        self.app.dispatch("admin", "/api/members", json.dumps(data).encode())
        with self.assertRaisesRegex(LabError, "unauthenticated"):
            self.app.actor(b"viewer")
        data.update(role="viewer", request_id="three")
        self.app.dispatch("admin", "/api/members", json.dumps(data).encode())
        self.assertEqual(self.app.actor(b"viewer"), "viewer")

    def test_management_scope_and_self_change(self):
        data = dict(target="admin", role=None, request_id="one", issued_at=100, lab_id="lab-1")
        with self.assertRaisesRegex(LabError, "self_change_denied"):
            self.app.dispatch("admin", "/api/members", json.dumps(data).encode())
        data.update(target="unregistered", request_id="two")
        with self.assertRaisesRegex(LabError, "scope_denied"):
            self.app.dispatch("admin", "/api/members", json.dumps(data).encode())

    def test_parser_and_routes(self):
        for data in [b"[]", b'{"x":1,"x":2}', b"\xff", b"x" * 4097]:
            with self.assertRaises(LabError):
                object_json(data)
        with self.assertRaisesRegex(LabError, "unknown_endpoint"):
            self.app.dispatch("op", "/unknown", b"{}")
        self.assertIn("events", self.app.dispatch("viewer", "/api/audit", b"{}"))

    def test_containment_refuses_root(self):
        with patch("mocklab.containment.os.getuid", return_value=0):
            with self.assertRaisesRegex(LabError, "containment_required"):
                verify()

    def test_membership_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = Journal(directory, "lab-1")
            lab = Lab(
                "lab-1",
                {"admin": "lab-admin", "viewer": "viewer"},
                journal=journal,
                clock=lambda: 100,
            )
            lab.manage("admin", "viewer", "operator", "one", 100)
            journal.close()
            journal = Journal(directory, "lab-1")
            self.addCleanup(journal.close)
            lab = Lab(
                "lab-1",
                {"admin": "lab-admin", "viewer": "viewer"},
                journal=journal,
                clock=lambda: 100,
            )
            self.assertEqual(lab._memberships["viewer"], "operator")
            with self.assertRaisesRegex(LabError, "replay_denied"):
                lab.manage("admin", "viewer", None, "one", 100)
