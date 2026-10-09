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

- [x] Owner authorized merging and a release after acceptance.
- [x] Real Firefox/native mTLS acceptance and Python 3.12.15 security-patch adoption.
- [x] Full application-image CVE/SBOM audit and dependency remediation.
- [ ] Publish stable source release after final merge-commit CI gates.
- [x] Update Cloud install/start instructions, republish and verify a new restored task.
- [x] Test real browser mTLS/visual interaction in CI's isolated namespace, without ports.

These adoption tasks are not claimed by local tests or HTTP asset checks.
Full production C2, real agents, public hosting, arbitrary commands, stealth,
persistence and defense bypass are excluded. Multi-agent scale, audit archival and
external identity providers require a separate future scope and threat review.

## Source release

Version metadata `0.1.0`; release publication requires all main-commit smoke,
container/browser and image-audit jobs. See [RELEASE.md](RELEASE.md) and
[STABLE-ACCEPTANCE.md](STABLE-ACCEPTANCE.md). GitHub Releases is authoritative
for actual publication status. The independent Cloud restoration evidence
remains historical rc.1/Python 3.12.14.
