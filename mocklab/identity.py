"""Ephemeral in-process identities; tokens never persisted or returned in diagnostics."""

import hashlib
import secrets
import time
from dataclasses import dataclass

from .core import ROLES, LabError, identifier, number


@dataclass(frozen=True)
class Identity:
    actor: str
    lab: str
    role: str
    expires: float


class Identities:
    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self._tokens = {}

    def issue(self, actor, lab, role, ttl=600):
        identifier(actor)
        identifier(lab)
        if (
            type(role) is not str
            or role not in ROLES
            or type(ttl) is not int
            or not 1 <= ttl <= 3600
        ):
            raise LabError("invalid_identity")
        if len(self._tokens) >= 100:
            raise LabError("identity_capacity")
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).digest()
        self._tokens[digest] = Identity(actor, lab, role, number(self._clock()) + ttl)
        return token

    def resolve(self, token, lab):
        if type(token) is not str or not 40 <= len(token) <= 64:
            raise LabError("unauthenticated")
        identity = self._tokens.get(hashlib.sha256(token.encode()).digest())
        if identity is None or number(self._clock()) >= identity.expires or identity.lab != lab:
            raise LabError("unauthenticated")
        return identity

    def revoke(self, token):
        if type(token) is not str:
            raise LabError("unauthenticated")
        self._tokens.pop(hashlib.sha256(token.encode()).digest(), None)


class Session:
    """No transport: trusted setup issues tokens and assigns Lab memberships."""

    def __init__(self, lab, identities, *, burst=100):
        if type(burst) is not int or not 1 <= burst <= 1000:
            raise LabError("invalid_limit")
        self.lab = lab
        self.identities = identities
        self._burst = burst
        self._counts = {}

    def execute(self, token, payload):
        identity = self.identities.resolve(token, self.lab.lab_id)
        if self.lab._memberships.get(identity.actor) != identity.role:
            raise LabError("unauthorized")
        if identity.actor not in self._counts and len(self._counts) >= 100:
            raise LabError("session_capacity")
        count = self._counts.get(identity.actor, 0)
        if count >= self._burst:
            raise LabError("session_capacity")
        self._counts[identity.actor] = count + 1
        return self.lab.execute(identity.actor, payload)
