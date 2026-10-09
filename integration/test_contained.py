"""Run only in the inspected, network-none CI container, with disposable PKI."""

import http.client
import json
import os
import socket
import ssl
import subprocess
import sys
import time
import unittest
import uuid
from pathlib import Path

from mocklab.containment import verify

ROOT = Path("/run/lab")


def context(actor):
    result = ssl.create_default_context(cafile=ROOT / "ca.crt")
    result.minimum_version = ssl.TLSVersion.TLSv1_3
    if actor:
        result.load_cert_chain(ROOT / f"{actor}.crt", ROOT / f"{actor}.key")
    return result


def request(actor, method, path, data=None, headers=None):
    conn = http.client.HTTPSConnection("127.0.0.1", 8443, context=context(actor), timeout=5)
    try:
        body = json.dumps(data).encode() if data is not None else None
        conn.request(method, path, body, headers or {"Content-Type": "application/json"})
        response = conn.getresponse()
        return response.status, response.read()
    finally:
        conn.close()


def envelope(operation="ping", **updates):
    data = dict(
        schema_version=1,
        request_id=uuid.uuid4().hex,
        lab_id="synthetic-lab",
        agent_id="mock-1",
        operation=operation,
        issued_at=time.time(),
    )
    data.update(updates)
    return data


class ContainedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify()
        cls.server = subprocess.Popen(
            [sys.executable, "-m", "mocklab.server"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        for _ in range(50):
            if cls.server.poll() is not None:
                raise RuntimeError(
                    "Contained server startup failed: " + cls.server.stderr.read().decode()
                )
            try:
                if request("admin", "GET", "/api/session")[0] == 200:
                    return
            except OSError:
                time.sleep(0.1)
        cls.server.terminate()
        raise RuntimeError("Contained server startup timed out")

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait(timeout=5)
        # Confirm the listener is gone, without scanning any network.
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", 8443)) == 0:
                raise RuntimeError("Listener survived cleanup")

    def test_01_isolation(self):
        verify()
        self.assertNotEqual(os.getuid(), 0)
        # Documentation-only address and numeric DNS packet destination, under network none.
        for family, address in [
            (socket.AF_INET, ("192.0.2.1", 53)),
            (socket.AF_INET6, ("2001:db8::1", 53)),
        ]:
            with socket.socket(family, socket.SOCK_DGRAM) as sock:
                with self.assertRaises(OSError):
                    sock.sendto(b"synthetic-dns-probe", address)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            with self.assertRaises(OSError):
                sock.connect(("192.0.2.1", 443))

    def test_02_mtls_and_ui(self):
        with self.assertRaises((OSError, http.client.HTTPException)):
            request(None, "GET", "/")
        code, body = request("viewer", "GET", "/")
        self.assertEqual(code, 200)
        self.assertIn(b"Mock Lab", body)
        self.assertEqual(request("viewer", "GET", "/app.js")[0], 200)
        self.assertEqual(request("viewer", "GET", "/style.css")[0], 200)
        code, body = request("viewer", "GET", "/api/session", headers={"Host": "wrong.invalid"})
        self.assertEqual(code, 403)
        self.assertIn(b"invalid_host", body)

    def test_03_rbac_replay_and_scope(self):
        self.assertEqual(request("viewer", "POST", "/api/execute", envelope())[0], 403)
        data = envelope()
        self.assertEqual(request("operator", "POST", "/api/execute", data)[0], 200)
        self.assertIn(b"replay_denied", request("operator", "POST", "/api/execute", data)[1])
        self.assertEqual(
            request("operator", "POST", "/api/execute", envelope(lab_id="other"))[0], 403
        )
        self.assertEqual(request("operator", "POST", "/api/execute", envelope("shell"))[0], 403)

    def test_04_management(self):
        data = dict(
            target="viewer",
            role="operator",
            request_id=uuid.uuid4().hex,
            issued_at=time.time(),
            lab_id="synthetic-lab",
        )
        self.assertEqual(request("operator", "POST", "/api/members", data)[0], 403)
        self.assertEqual(request("admin", "POST", "/api/members", data)[0], 200)
        self.assertEqual(request("viewer", "POST", "/api/execute", envelope())[0], 200)
        data.update(role=None, request_id=uuid.uuid4().hex)
        self.assertEqual(request("admin", "POST", "/api/members", data)[0], 200)
        self.assertEqual(request("viewer", "GET", "/api/session")[0], 403)
        data.update(role="viewer", request_id=uuid.uuid4().hex)
        self.assertEqual(request("admin", "POST", "/api/members", data)[0], 200)

    def test_05_lifecycle_audit_and_restart(self):
        self.assertEqual(
            request(
                "operator",
                "POST",
                "/api/execute",
                envelope("emit_test_event", fixture_id="synthetic-login"),
            )[0],
            200,
        )
        self.assertEqual(request("operator", "POST", "/api/execute", envelope("stop"))[0], 200)
        self.assertIn(b"agent_stopped", request("operator", "POST", "/api/execute", envelope())[1])
        code, body = request("viewer", "POST", "/api/audit", {})
        self.assertEqual(code, 200)
        self.assertGreater(len(json.loads(body)["events"]), 10)
        self.server.terminate()
        self.server.wait(timeout=5)
        type(self).server = subprocess.Popen(
            [sys.executable, "-m", "mocklab.server"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        for _ in range(50):
            try:
                code, body = request("operator", "POST", "/api/execute", envelope("status"))
                if code == 200:
                    self.assertIn(b"stopped", body)
                    return
            except OSError:
                time.sleep(0.1)
        self.fail("Recovery failed")


if __name__ == "__main__":
    unittest.main()
