# Threat Model

Assets: lab isolation, synthetic memberships, bounded mock lifecycle and audit
integrity/availability. Trust: host/container operator and lab CA issuer. Client
messages, browser fields and certificates from unregistered peers are untrusted.
Production data and operational targets are not permitted.

| Threat | Implemented control | Evidence |
| --- | --- | --- |
| Public listener / egress | Fixed loopback; topology guard; network none; no ports | Docker inspect + contained IPv4/IPv6 TCP/UDP tests |
| Identity spoof / expired session | TLS 1.3 mTLS; fingerprint pinning; 600s session | TLS and unit expiry tests |
| Escalation / cross-lab | Server-side current membership; default deny; scope check | Role matrix, management/revoke/scope tests |
| Arbitrary execution | Fixed four operations and fixture ID; no agent OS access | Schema and OS-call guard tests |
| Replay / restart reset | Time window and durable accepted IDs | Unit + restart recovery tests |
| Audit loss / crash | FULL-sync commits; fail closed; incomplete recovery blocks | Storage failure/recovery tests |
| Traversal / browser injection | Fixed assets; textContent; no external assets; Host/Origin/CSP | Route tests and HTTP asset checks |
| Resource exhaustion | Payload/header/time/budget/agent/audit limits; container bounds | Negative and capacity tests |
| Git disclosure | Disposable PKI outside Git/image; no diagnostic secrets | Smoke signatures + diff review |

Residual risks: malicious host/CA owner; local caller modifying Python internals;
storage hardware failures; denied TLS connections not durably recorded; attacker
exhausting bounded lab availability; wall-clock anomalies for envelope validity.
SQLite is not tamper-proof. No production availability or multi-tenant guarantees.

A host browser cannot access a network-none container; exposing a port is not an
approved workaround. The UI needs a trusted same-namespace browser and enrolled
certificate. CI checks HTTP asset delivery/API workflow; full visual browser/mTLS
interaction in a separate VM requires environment-specific operational acceptance.

Tests use only disposable identities and documentation-only numeric endpoints in
network-none containers. They do not scan third-party systems. See
[VALIDATION.md](VALIDATION.md) for exact acceptance scope.
