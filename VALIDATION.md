# Validation and acceptance

## Local checks

CPython 3.12.14: 33 tests (30 core/CLI/API and 3 release-publication tests),
4 development smoke checks,
Ruff 0.16.10 lint/format, shell syntax and whitespace checks passed.
No listener started in the ordinary workspace. Core and dispatch tests are in-process.

## Container acceptance

GitHub Actions performs a separate Docker job: build digest-pinned Python image,
inspect network none/non-root/read-only/capabilities/ports/mounts/resource bounds,
provision one-day synthetic PKI into private tmpfs, then run contained integration.

Tests: egress refusal to documentation-only IPv4/IPv6 addresses (TCP and DNS-port UDP),
mTLS refusal without certificate, UI asset delivery, Host validation, RBAC, lab scope,
replay, management/revocation, mock lifecycle, audit, restart recovery and listener cleanup.
Certificate validity is also enforced by OpenSSL; application expiry tested in-process.

All five contained integration tests passed in GitHub Actions run
[37889473519](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37889473519)
on 2026-10-09. Smoke/unit/lint job passed as well. Provisioning failures were
corrected by streaming selected fixture files into private tmpfs through the
unprivileged container process, without relaxing storage/network controls.
The CA signing key stays on the fixture host and is not transferred to the container.

## Scope of completion

Implementation scope: one-agent educational mock MVP, offline CLI, in-process core,
loopback mTLS API, local UI, roles, durable audit, containment acceptance scripts and CI.
Production scale, real agents, public hosting and arbitrary execution are excluded.

Browser visual/mTLS testing in a user-managed isolated VM is not claimed by HTTP asset
acceptance. CI validates API/asset behavior. Codex Cloud remains a development-only
workspace with independent containment unverified; no listener runs there. Its setup
was updated to the exact release commit using a verified local Git bundle, without
network-policy expansion. Repeated setup passed 33 tests, 4 smoke, lint/format, CLI
and expected server refusal. Publication/restoration status and runtime review:
[ACCEPTANCE-2026-10-09.md](ACCEPTANCE-2026-10-09.md).
Release candidate v0.1.0-rc.1 was published after successful main-commit
smoke/container jobs. The tag and release target were read back and match
c27150a2c0fa3280208f0efe8afa9adb3178a4da. This is not stable/production acceptance.

## Stable promotion checks under implementation

The development runtime is Python 3.12.15. Trivy 0.75.0 produces full CVE JSON
and CycloneDX SBOM; all HIGH/CRITICAL findings block publication, including
unfixed findings. A pinned Firefox image shares only the inspected application
network namespace. Native NSS trusts the disposable CA and imports each client
identity. Tests require refusal without identity or with an untrusted CA and
verify viewer/operator/admin UI, audit and role changes. No TLS bypass or port
publishing is enabled. These new checks are not yet recorded as passed.
