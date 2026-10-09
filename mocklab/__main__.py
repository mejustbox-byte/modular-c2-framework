"""One deterministic offline exercise; never opens sockets or prints credentials."""

import argparse
import json
import sqlite3
import tempfile
import time
import uuid
from pathlib import Path

from .config import Config
from .core import Lab, LabError
from .identity import Identities, Session
from .storage import Journal


def run(directory, config, interactive=False):
    journal = Journal(directory, config.lab_id, limit=config.max_events)
    try:
        lab = Lab(
            config.lab_id,
            {"synthetic-operator": "operator"},
            journal=journal,
            max_events=config.max_events,
            max_requests=config.max_requests,
        )
        identities = Identities()
        token = identities.issue("synthetic-operator", lab.lab_id, "operator")
        session = Session(lab, identities, burst=config.burst)

        def operations():
            if not interactive:
                yield from ("status", "ping", "emit_test_event", "stop", "status")
                return
            choices = {"1": "status", "2": "ping", "3": "emit_test_event", "4": "stop"}
            print("Offline mock lab: 1 status, 2 ping, 3 synthetic event, 4 stop, 5 audit, 0 exit")
            while True:
                try:
                    choice = input("Operation: ").strip()
                except EOFError:
                    return
                if choice == "0":
                    return
                if choice == "5":
                    for event in lab.audit("synthetic-operator"):
                        print(json.dumps(event))
                    continue
                if choice not in choices:
                    print("Choose 0–5")
                    continue
                yield choices[choice]

        for operation in operations():
            request = dict(
                schema_version=1,
                request_id=uuid.uuid4().hex,
                lab_id=lab.lab_id,
                agent_id="mock-1",
                operation=operation,
                issued_at=time.time(),
            )
            if operation == "emit_test_event":
                request["fixture_id"] = "synthetic-login"
            try:
                result = session.execute(token, json.dumps(request).encode())
            except LabError as error:
                if not interactive:
                    raise
                print(json.dumps({"operation": operation, "error": str(error)}))
                continue
            print(json.dumps({"operation": operation, "result": result}))
        identities.revoke(token)
        print(
            json.dumps(
                {"audit_records": len(lab.audit("synthetic-operator")), "identity_revoked": True}
            )
        )
    finally:
        journal.close()


def main():
    parser = argparse.ArgumentParser(description="Offline synthetic mock exercise; no listeners")
    parser.add_argument(
        "--audit-directory", help="Existing private directory (mode 0700), fresh journal"
    )
    parser.add_argument("--config", help="Strict TOML configuration, up to 4096 bytes")
    parser.add_argument("--interactive", action="store_true", help="Fixed-operation terminal menu")
    args = parser.parse_args()
    try:
        config = Config()
        if args.config:
            with Path(args.config).open("rb") as file:
                config = Config.parse(file.read(4097))
        if args.audit_directory:
            run(args.audit_directory, config, args.interactive)
        else:
            with tempfile.TemporaryDirectory(prefix="mocklab-") as directory:
                run(directory, config, args.interactive)
    except (LabError, OSError, sqlite3.Error) as error:
        parser.exit(
            1, f"Exercise refused: {error if isinstance(error, LabError) else 'storage_error'}\n"
        )


if __name__ == "__main__":
    main()
