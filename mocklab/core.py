"""Bounded, single-threaded mock core; caller supplies trusted identity, never a role."""

import json
import math
import re
import time
from dataclasses import dataclass

ID = re.compile(r"[a-zA-Z0-9_-]{1,64}\Z")
OPERATIONS = frozenset({"ping", "status", "emit_test_event", "stop"})
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
            data = json.loads(payload, object_pairs_hook=unique)
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

    def __init__(self, lab_id, memberships, *, max_events=1000, max_requests=1000, clock=time.time):
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

    def _audit(self, actor, request, outcome, reason):
        if len(self._events) >= self._max_events:
            raise LabError("audit_full")
        self._events.append(
            {
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
        )

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
            self._audit(actor, request, "denied", str(error))
            raise
        self._audit(actor, request, "allowed", "authorized")
        self._seen.add(request.request_id)
        if request.operation == "stop":
            self._stopped = True
        result = {
            "ping": {"reply": "pong"},
            "status": {"state": "stopped" if self._stopped else "ready"},
            "emit_test_event": {"fixture_id": "synthetic-login", "event": "mock_login"},
            "stop": {"state": "stopped"},
        }[request.operation]
        try:
            self._audit(actor, request, "completed", "mock_completed")
        except Exception:
            self._blocked = True
            raise LabError("audit_failed") from None
        return result
