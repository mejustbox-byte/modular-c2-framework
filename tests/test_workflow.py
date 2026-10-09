import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_core import payload

from mocklab import Lab, LabError
from mocklab.identity import Identities, Session
from mocklab.storage import Journal


class WorkflowTests(unittest.TestCase):
    def test_identity_expiry_revocation_scope_and_capacity(self):
        now = [100]
        identities = Identities(clock=lambda: now[0])
        token = identities.issue("op", "lab-1", "operator", ttl=10)
        self.assertEqual(identities.resolve(token, "lab-1").actor, "op")
        for invalid in ["wrong", "x" * 43, None]:
            with self.assertRaisesRegex(LabError, "unauthenticated"):
                identities.resolve(invalid, "lab-1")
        with self.assertRaises(LabError):
            identities.resolve(token, "lab-2")
        now[0] = 110
        with self.assertRaises(LabError):
            identities.resolve(token, "lab-1")
        identities.revoke(token)
        now[0] = 100
        with self.assertRaises(LabError):
            identities.resolve(token, "lab-1")
        for _ in range(100):
            identities.issue("op", "lab-1", "operator")
        with self.assertRaisesRegex(LabError, "identity_capacity"):
            identities.issue("op", "lab-1", "operator")

    def test_session_role_mismatch_and_burst(self):
        identities = Identities()
        lab = Lab("lab-1", {"op": "viewer"}, clock=lambda: 100)
        session = Session(lab, identities, burst=1)
        wrong = identities.issue("op", "lab-1", "operator")
        with self.assertRaisesRegex(LabError, "unauthorized"):
            session.execute(wrong, payload())
        token = identities.issue("op", "lab-1", "viewer")
        session.execute(token, payload("status"))
        with self.assertRaisesRegex(LabError, "session_capacity"):
            session.execute(token, payload("status", request_id="two"))

    def test_journal_replay_and_lifecycle_survive_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = Journal(directory, "lab-1")
            lab = Lab("lab-1", {"op": "operator"}, journal=journal, clock=lambda: 100)
            lab.execute("op", payload("stop"))
            journal.close()
            journal = Journal(directory, "lab-1")
            self.addCleanup(journal.close)
            recovered = Lab("lab-1", {"op": "operator"}, journal=journal, clock=lambda: 100)
            with self.assertRaisesRegex(LabError, "replay"):
                recovered.execute("op", payload("stop"))
            with self.assertRaisesRegex(LabError, "agent_stopped"):
                recovered.execute("op", payload(request_id="two"))
            self.assertEqual(
                recovered.execute("op", payload("status", request_id="three")), {"state": "stopped"}
            )

    def test_interrupted_operation_blocks_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = Journal(directory, "lab-1")
            lab = Lab("lab-1", {"op": "operator"}, journal=journal, clock=lambda: 100)
            original = journal.append

            def fail(event):
                if event["outcome"] == "completed":
                    raise OSError("synthetic")
                original(event)

            with patch.object(journal, "append", side_effect=fail):
                with self.assertRaisesRegex(LabError, "audit_failed"):
                    lab.execute("op", payload("stop"))
            journal.close()
            journal = Journal(directory, "lab-1")
            self.addCleanup(journal.close)
            recovered = Lab("lab-1", {"op": "operator"}, journal=journal, clock=lambda: 100)
            with self.assertRaisesRegex(LabError, "audit_blocked"):
                recovered.execute("op", payload("status", request_id="two"))

    def test_private_storage_required(self):
        with tempfile.TemporaryDirectory() as directory:
            os.chmod(directory, 0o755)
            with self.assertRaisesRegex(LabError, "unsafe_audit_directory"):
                Journal(directory, "lab-1")
            os.chmod(directory, 0o700)
            (Path(directory) / "audit.sqlite3").symlink_to("target")
            with self.assertRaisesRegex(LabError, "unsafe_audit_file"):
                Journal(directory, "lab-1")

    def test_journal_scope_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = Journal(directory, "lab-1")
            with self.assertRaisesRegex(LabError, "journal_scope_mismatch"):
                Lab("lab-2", {}, journal=journal)
            journal.close()
            with self.assertRaisesRegex(LabError, "journal_scope_mismatch"):
                Journal(directory, "lab-2")

    def test_durable_capacity_prevents_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = Journal(directory, "lab-1", limit=2)
            self.addCleanup(journal.close)
            lab = Lab("lab-1", {"op": "operator"}, journal=journal, max_events=2, clock=lambda: 100)
            lab.execute("op", payload())
            with self.assertRaisesRegex(LabError, "audit_full"):
                lab.execute("op", payload("stop", request_id="two"))
            self.assertFalse(lab._stopped)
            self.assertEqual(len(journal.events()), 2)

    def test_corrupt_journal_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = Journal(directory, "lab-1")
            lab = Lab("lab-1", {"op": "operator"}, journal=journal, clock=lambda: 100)
            lab.execute("op", payload())
            journal.close()
            db = sqlite3.connect(Path(directory) / "audit.sqlite3")
            with db:
                db.execute("UPDATE events SET body=? WHERE seq=1", (json.dumps({}),))
            db.close()
            journal = Journal(directory, "lab-1")
            self.addCleanup(journal.close)
            with self.assertRaisesRegex(LabError, "journal_corrupt"):
                Lab("lab-1", {"op": "operator"}, journal=journal)

    def test_utf16_not_accepted_as_utf8(self):
        encoded = payload().decode().encode("utf-16")
        lab = Lab("lab-1", {"op": "operator"})
        with self.assertRaisesRegex(LabError, "invalid_json"):
            lab.execute("op", encoded)


class ConfigTests(unittest.TestCase):
    def test_valid_and_invalid_config(self):
        from mocklab.config import Config

        self.assertEqual(Config.parse(b'lab_id="lab-1"').lab_id, "lab-1")
        for data in [
            b"max_events=true",
            b'bind_address="0.0.0.0"',
            b"burst=0",
            b'lab_id="../secret"',
            b"x" * 4097,
            b"\xff",
            b'lab_id="one"\nlab_id="two"',
        ]:
            with self.subTest(data=data), self.assertRaises(LabError):
                Config.parse(data)


class CommandTests(unittest.TestCase):
    def test_offline_command_and_restart_refusal(self):
        import subprocess
        import sys

        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-m", "mocklab", "--audit-directory", directory],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual(rows[-1], {"audit_records": 10, "identity_revoked": True})
            self.assertEqual(rows[-2]["result"], {"state": "stopped"})
            retry = subprocess.run(
                [sys.executable, "-m", "mocklab", "--audit-directory", directory],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(retry.returncode, 1)
            self.assertIn("agent_stopped", retry.stderr)

    def test_interactive_menu(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "mocklab", "--interactive"],
            input="wrong\n2\n5\n4\n0\n",
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pong", result.stdout)
        self.assertIn('"outcome": "completed"', result.stdout)
        self.assertIn('"identity_revoked": true', result.stdout)
