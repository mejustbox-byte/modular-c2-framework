# Roadmap

Scope: bounded one-agent educational mock MVP. Checkboxes require implementation
and evidence; release/merge is separate from implementation.

## MVP implementation

- [x] Core docs, stack, lockfile, CI and separate private Codex Cloud.
- [x] Strict versioned envelope/config, fixed operations and synthetic fixtures.
- [x] Mock lifecycle, bounded payload/agent/audit/replay/request budget.
- [x] Server-side RBAC and lab scope; pre-enrolled membership management/revocation.
- [x] Loopback TLS 1.3 API, mTLS verification/pinning and application expiry.
- [x] SQLite audit, correlation, durability and fail-closed recovery.
- [x] Local web UI and offline CLI/menu.
- [x] Non-root read-only network-none container configuration and runtime guard.
- [x] Unit/negative/CLI/restart tests and automated container acceptance workflow.
- [x] Latest Docker CI acceptance fully passed and recorded in VALIDATION.md.

## Operational adoption

- [ ] Review draft PR chain and merge only when authorized.
- [ ] Update Cloud install/start instructions from old pinned setup commit after review.
- [ ] Test browser mTLS/visual interaction in the user's isolated VM, with no port exposure.

These adoption tasks are not claimed by local tests or HTTP asset checks.
Full production C2, real agents, public hosting, arbitrary commands, stealth,
persistence and defense bypass are excluded. Multi-agent scale, audit archival and
external identity providers require a separate future scope and threat review.
