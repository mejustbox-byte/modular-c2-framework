"""Single-threaded loopback-only mTLS mock API, refusing uncontained runtime."""

import argparse
import hashlib
import json
import sqlite3
import ssl
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .containment import verify
from .core import Lab, LabError, identifier, number
from .storage import Journal


def object_json(body):
    if type(body) is not bytes or len(body) > 4096:
        raise LabError("invalid_payload")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise LabError("duplicate_field")
            result[key] = value
        return result

    try:
        data = json.loads(body.decode("utf-8"), object_pairs_hook=unique)
    except (ValueError, UnicodeError, RecursionError):
        raise LabError("invalid_json") from None
    if type(data) is not dict:
        raise LabError("invalid_schema")
    return data


class Application:
    def __init__(self, lab, principals, clock=time.monotonic):
        self.lab = lab
        self.principals = dict(principals)
        self.clock = clock
        self.expiry = clock() + 600
        self.counts = {}

    def actor(self, certificate):
        actor = self.principals.get(hashlib.sha256(certificate).hexdigest())
        if actor is None or self.clock() >= self.expiry or actor not in self.lab._memberships:
            raise LabError("unauthenticated")
        return actor

    def dispatch(self, actor, path, body):
        count = self.counts.get(actor, 0)
        if count >= 100:
            raise LabError("session_capacity")
        self.counts[actor] = count + 1
        if path == "/api/execute":
            return self.lab.execute(actor, body)
        if path == "/api/audit":
            if body != b"{}":
                raise LabError("invalid_schema")
            return {"events": self.lab.audit(actor)}
        if path == "/api/members":
            data = object_json(body)
            if data.keys() != {"target", "role", "request_id", "issued_at", "lab_id"}:
                raise LabError("invalid_schema")
            target = identifier(data["target"])
            role = data["role"]
            if type(role) not in (str, type(None)):
                raise LabError("invalid_role")
            if data["lab_id"] != self.lab.lab_id or target not in self.principals.values():
                raise LabError("scope_denied")
            return self.lab.manage(
                actor, target, role, identifier(data["request_id"]), number(data["issued_at"])
            )
        raise LabError("unknown_endpoint")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *args):
        pass  # Never log headers, credentials or attacker-controlled paths.

    def reply(self, code, content, mime="application/json"):
        if not isinstance(content, bytes):
            content = json.dumps(content, allow_nan=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; frame-ancestors 'none'; object-src 'none'",
        )
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(content)
        self.close_connection = True

    def authenticate(self):
        verify()
        allowed_host = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get_all("Host") != [allowed_host]:
            raise LabError("invalid_host")
        origin = self.headers.get_all("Origin")
        if origin is not None and origin != [f"https://{allowed_host}"]:
            raise LabError("invalid_origin")
        if sum(len(k) + len(v) for k, v in self.headers.items()) > 8192:
            raise LabError("invalid_headers")
        return self.server.app.actor(self.connection.getpeercert(binary_form=True))

    def do_GET(self):
        try:
            actor = self.authenticate()
            if self.path == "/api/session":
                self.reply(
                    200,
                    {
                        "actor_id": actor,
                        "role": self.server.app.lab._memberships[actor],
                        "lab_id": self.server.app.lab.lab_id,
                    },
                )
                return
            assets = {
                "/": ("index.html", "text/html; charset=utf-8"),
                "/app.js": ("app.js", "text/javascript"),
                "/style.css": ("style.css", "text/css"),
            }
            if self.path not in assets:
                raise LabError("unknown_endpoint")
            name, mime = assets[self.path]
            self.reply(200, (Path(__file__).parent / "web" / name).read_bytes(), mime)
        except LabError as error:
            self.reply(403, {"error": str(error)})

    def do_POST(self):
        try:
            actor = self.authenticate()
            lengths = self.headers.get_all("Content-Length")
            if self.headers.get("Transfer-Encoding") or lengths is None or len(lengths) != 1:
                raise LabError("invalid_length")
            if not lengths[0].isdigit() or not 0 <= int(lengths[0]) <= 4096:
                raise LabError("invalid_length")
            if self.headers.get_all("Content-Type") != ["application/json"]:
                raise LabError("invalid_content_type")
            body = self.rfile.read(int(lengths[0]))
            if len(body) != int(lengths[0]):
                raise LabError("invalid_length")
            result = self.server.app.dispatch(actor, self.path, body)
            self.reply(200, result)
        except LabError as error:
            self.reply(403, {"error": str(error)})
        except (OSError, ValueError, sqlite3.Error):
            self.reply(503, {"error": "service_unavailable"})


class Server(HTTPServer):
    request_queue_size = 5

    def __init__(self, port, app, context):
        verify()
        if type(port) is not int or not 1024 <= port <= 65535:
            raise LabError("invalid_port")
        self.app = app
        self.context = context
        super().__init__(("127.0.0.1", port), Handler)

    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(3)
        try:
            return self.context.wrap_socket(connection, server_side=True), address
        except Exception:
            connection.close()
            raise

    def handle_error(self, request, client_address):
        pass


def main():
    parser = argparse.ArgumentParser(description="Contained loopback mTLS mock laboratory")
    parser.add_argument("--directory", default="/run/lab")
    parser.add_argument("--port", type=int, default=8443)
    args = parser.parse_args()
    journal = None
    try:
        verify()
        directory = Path(args.directory)
        enrolled = object_json((directory / "principals.json").read_bytes())
        if enrolled.keys() != {"lab_id", "principals"} or type(enrolled["principals"]) is not list:
            raise LabError("invalid_principals")
        if not 1 <= len(enrolled["principals"]) <= 100:
            raise LabError("invalid_principals")
        members, principals = {}, {}
        for identity in enrolled["principals"]:
            if type(identity) is not dict or identity.keys() != {"actor", "role", "fingerprint"}:
                raise LabError("invalid_principals")
            actor = identifier(identity["actor"])
            fingerprint = identity["fingerprint"]
            if (
                type(fingerprint) is not str
                or len(fingerprint) != 64
                or any(c not in "0123456789abcdef" for c in fingerprint)
                or fingerprint in principals
                or actor in members
            ):
                raise LabError("invalid_principals")
            members[actor] = identity["role"]
            principals[fingerprint] = actor
        journal = Journal(directory, identifier(enrolled["lab_id"]))
        lab = Lab(enrolled["lab_id"], members, journal=journal)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(directory / "ca.crt")
        context.load_cert_chain(directory / "server.crt", directory / "server.key")
        with Server(args.port, Application(lab, principals), context) as server:
            server.serve_forever(poll_interval=0.1)
    except (LabError, OSError, ValueError, sqlite3.Error):
        parser.exit(1, "Laboratory startup refused; check containment and private configuration.\n")
    finally:
        if journal is not None:
            journal.close()


if __name__ == "__main__":
    main()
