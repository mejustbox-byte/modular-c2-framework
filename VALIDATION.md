# Validation and acceptance

## Local checks

CPython 3.12.14: 30 unit/negative/restart/CLI/API tests, 4 development smoke checks,
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
[37888647153](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37888647153)
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
was checked on PR #1, new branch install/start instructions need review before adoption.
All PRs remain drafts without merging; main does not yet contain the implementation.
