"""Bounded, single-threaded mock core; caller supplies trusted identity, never a role."""

import json
import math
import re
import time
from dataclasses import dataclass

ID = re.compile(r"[a-zA-Z0-9_-]{1,64}\Z")
OPERATIONS = frozenset({"ping", "status", "emit_test_event", "stop"})
MANAGEMENT = frozenset({"set_viewer", "set_operator", "set_lab_admin", "revoke_member"})
ROLES = frozenset({"viewer", "operator", "lab-admin"})


class LabError(Exception):
    """Fixed reason code only; never include untrusted input in diagnostics."""


def identifier(value):
    if type(value) is not str or not ID.fullmatch(value):
        raise LabError("invalid_id")
    return value


def number(value):
    if type(value) not in (int, float):
        raise LabError("invalid_time")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise LabError("invalid_time")
    return value


@dataclass(frozen=True)
class Request:
    request_id: str
    lab_id: str
    agent_id: str
    operation: str
    issued_at: float
    fixture_id: str | None = None

    @classmethod
    def parse(cls, payload):
        if type(payload) is not bytes or len(payload) > 4096:
            raise LabError("invalid_payload")

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise LabError("duplicate_field")
                result[key] = value
            return result

        try:
            data = json.loads(payload.decode("utf-8"), object_pairs_hook=unique)
        except (ValueError, UnicodeError, RecursionError):
            raise LabError("invalid_json") from None
        required = {"schema_version", "request_id", "lab_id", "agent_id", "operation", "issued_at"}
        if type(data) is not dict or not required <= data.keys():
            raise LabError("invalid_schema")
        if data.keys() - (required | {"fixture_id"}):
            raise LabError("unknown_field")
        if type(data["schema_version"]) is not int or data["schema_version"] != 1:
            raise LabError("invalid_version")
        op = data["operation"]
        if type(op) is not str or op not in OPERATIONS:
            raise LabError("invalid_operation")
        fixture = data.get("fixture_id")
        if op == "emit_test_event":
            if fixture != "synthetic-login":
                raise LabError("invalid_fixture")
        elif "fixture_id" in data:
            raise LabError("unexpected_fixture")
        return cls(
            identifier(data["request_id"]),
            identifier(data["lab_id"]),
            identifier(data["agent_id"]),
            op,
            number(data["issued_at"]),
            fixture,
        )


class Lab:
    """Trusted in-process adapter only, NOT authentication or containment.

    No sockets, subprocesses, filesystem operations or dynamic code loading.
    A new Lab creates one synthetic agent. Storage is bounded and never evicted
    automatically. A fresh instance is required when storage fills.
    """

    def __init__(
        self,
        lab_id,
        memberships,
        *,
        max_events=1000,
        max_requests=1000,
        clock=time.time,
        journal=None,
    ):
        self.lab_id = identifier(lab_id)
        if type(memberships) is not dict or len(memberships) > 100:
            raise LabError("invalid_memberships")
        self._memberships = {}
        for actor, role in memberships.items():
            identifier(actor)
            if type(role) is not str or role not in ROLES:
                raise LabError("invalid_role")
            self._memberships[actor] = role
        for limit in (max_events, max_requests):
            if type(limit) is not int or not 2 <= limit <= 10000:
                raise LabError("invalid_limit")
        self._max_events = max_events
        self._max_requests = max_requests
        self._clock = clock
        self._events = []
        self._seen = set()
        self._stopped = False
        self._blocked = False
        self._journal = journal
        if journal is not None:
            if journal.limit != max_events or journal.lab_id != self.lab_id:
                raise LabError("journal_scope_mismatch")
            self._events = journal.events()
            pending = {}
            for index, event in enumerate(self._events, 1):
                fields = {
                    "schema_version",
                    "event_id",
                    "timestamp_utc",
                    "actor_id",
                    "lab_id",
                    "request_id",
                    "agent_id",
                    "operation",
                    "outcome",
                    "reason_code",
                }
                if type(event) is not dict or event.keys() != fields:
                    raise LabError("journal_corrupt")
                if (
                    type(event["event_id"]) is not int
                    or event["event_id"] != index
                    or type(event["schema_version"]) is not int
                    or event["schema_version"] != 1
                ):
                    raise LabError("journal_corrupt")
                try:
                    identifier(event["actor_id"])
                    identifier(event["reason_code"])
                    number(event["timestamp_utc"])
                    if event["request_id"] is not None:
                        identifier(event["request_id"])
                    if event["agent_id"] is not None:
                        identifier(event["agent_id"])
                    if event["operation"] is not None:
                        if (
                            type(event["operation"]) is not str
                            or event["operation"] not in OPERATIONS | MANAGEMENT
                        ):
                            raise LabError("journal_corrupt")
                except LabError:
                    raise LabError("journal_corrupt") from None
                if event.get("lab_id") != self.lab_id:
                    raise LabError("journal_scope_mismatch")
                outcome = event.get("outcome")
                request_id = event.get("request_id")
                if outcome == "allowed":
                    identifier(request_id)
                    if request_id in self._seen:
                        raise LabError("journal_corrupt")
                    pending[request_id] = event.get("operation")
                    self._seen.add(request_id)
                elif outcome == "completed":
                    if request_id not in pending or event.get("operation") != pending[request_id]:
                        raise LabError("journal_corrupt")
                    del pending[request_id]
                    operation = event.get("operation")
                    if operation in MANAGEMENT:
                        target = identifier(event["agent_id"])
                        if operation == "revoke_member":
                            self._memberships.pop(target, None)
                        else:
                            self._memberships[target] = {
                                "set_viewer": "viewer",
                                "set_operator": "operator",
                                "set_lab_admin": "lab-admin",
                            }[operation]
                    if operation == "stop":
                        self._stopped = True
                elif outcome != "denied":
                    raise LabError("journal_corrupt")
            if len(self._seen) > self._max_requests:
                raise LabError("journal_corrupt")
            self._blocked = bool(pending)

    def _audit(self, actor, request, outcome, reason):
        if len(self._events) >= self._max_events:
            raise LabError("audit_full")
        event = {
            "schema_version": 1,
            "event_id": len(self._events) + 1,
            "timestamp_utc": number(self._clock()),
            "actor_id": actor,
            "lab_id": self.lab_id,
            "request_id": request.request_id if request else None,
            "agent_id": request.agent_id if request else None,
            "operation": request.operation if request else None,
            "outcome": outcome,
            "reason_code": reason,
        }
        if self._journal is not None:
            self._journal.append(event)
        self._events.append(event)

    def _record(self, actor, request, outcome, reason):
        try:
            self._audit(actor, request, outcome, reason)
        except Exception:
            self._blocked = True
            raise LabError("audit_failed") from None

    def audit(self, actor):
        identifier(actor)
        if actor not in self._memberships:
            raise LabError("unauthorized")
        return tuple(dict(event) for event in self._events)

    def execute(self, actor, payload):
        """actor must come from a trusted adapter, never from client JSON."""
        identifier(actor)
        if self._blocked:
            raise LabError("audit_blocked")
        # Reserve authorization + terminal records before any mock effect.
        if len(self._events) + 2 > self._max_events:
            raise LabError("audit_full")
        request = None
        try:
            request = Request.parse(payload)
            role = self._memberships.get(actor)
            if role is None or (role == "viewer" and request.operation != "status"):
                raise LabError("unauthorized")
            if request.lab_id != self.lab_id or request.agent_id != "mock-1":
                raise LabError("scope_denied")
            age = number(self._clock()) - request.issued_at
            if not 0 <= age <= 60:
                raise LabError("expired_request")
            if request.request_id in self._seen:
                raise LabError("replay_denied")
            if len(self._seen) >= self._max_requests:
                raise LabError("request_capacity")
            if self._stopped and request.operation != "status":
                raise LabError("agent_stopped")
        except LabError as error:
            self._record(actor, request, "denied", str(error))
            raise
        self._record(actor, request, "allowed", "authorized")
        self._seen.add(request.request_id)
        if request.operation == "stop":
            self._stopped = True
        result = {
            "ping": {"reply": "pong"},
            "status": {"state": "stopped" if self._stopped else "ready"},
            "emit_test_event": {"fixture_id": "synthetic-login", "event": "mock_login"},
            "stop": {"state": "stopped"},
        }[request.operation]
        self._record(actor, request, "completed", "mock_completed")
        return result

    def manage(self, actor, target, role, request_id, issued_at):
        """Admin-only role change/revocation of a pre-enrolled synthetic identity."""
        identifier(actor)
        identifier(target)
        identifier(request_id)
        number(issued_at)
        if role not in ("viewer", "operator", "lab-admin", None):
            raise LabError("invalid_role")
        operation = {
            "viewer": "set_viewer",
            "operator": "set_operator",
            "lab-admin": "set_lab_admin",
            None: "revoke_member",
        }[role]
        request = Request(request_id, self.lab_id, target, operation, issued_at)
        if self._blocked:
            raise LabError("audit_blocked")
        if len(self._events) + 2 > self._max_events:
            raise LabError("audit_full")
        try:
            if self._memberships.get(actor) != "lab-admin":
                raise LabError("unauthorized")
            if target == actor:
                raise LabError("self_change_denied")
            if not 0 <= number(self._clock()) - issued_at <= 60:
                raise LabError("expired_request")
            if request_id in self._seen:
                raise LabError("replay_denied")
            if len(self._seen) >= self._max_requests:
                raise LabError("request_capacity")
            if (
                role is not None
                and target not in self._memberships
                and len(self._memberships) >= 100
            ):
                raise LabError("membership_capacity")
        except LabError as error:
            self._record(actor, request, "denied", str(error))
            raise
        self._record(actor, request, "allowed", "authorized")
        self._seen.add(request_id)
        if role is None:
            self._memberships.pop(target, None)
        else:
            self._memberships[target] = role
        self._record(actor, request, "completed", "membership_changed")
        return {"actor_id": target, "role": role}
