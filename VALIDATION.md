# Validation and acceptance

## Development checks

CPython 3.12.15: 34 unit/negative/CLI/API/recovery/publication tests, 4 smoke
checks, Ruff 0.16.10 lint/format, shell syntax and whitespace checks pass locally.
No server listener starts in the ordinary workspace; startup refusal is expected.

## Container and real browser checks

CI builds the digest-pinned Python 3.12.15 Alpine runtime, verifies network none,
non-root/read-only/capability/port/mount/resource limits before listener startup,
and provisions disposable synthetic PKI into private tmpfs. Five integration
tests cover IPv4/IPv6/DNS-port UDP egress refusal to documentation-only addresses,
mTLS refusal without certificate, assets, Host, RBAC, lab scope, replay,
management/revocation, lifecycle, audit/restart recovery and listener cleanup.

Real headless Firefox runs in a separate pinned test container sharing only the
application network namespace. Native NSS imports the lab CA and each client
identity. HTTPS validation stays enabled. Tests refuse absent client identity
and an untrusted CA, render actual assets/JS, verify viewer/operator/admin
controls, exercise status/audit, and validate role changes and access revocation
through fresh browser sessions. Screenshots are CI artifacts; PKI is not exported.
Desktop screenshots were visually inspected for all controls and audit output.

## CVE and SBOM audit

Checksum-pinned Trivy 0.75.0 scans the complete application image and writes
full CVE JSON plus CycloneDX SBOM. All HIGH/CRITICAL findings block release,
including unfixed findings. No ignore file or suppression is used. Bookworm
was rejected with 53 HIGH and 2 CRITICAL findings. Alpine plus the zlib patch
and removal of unused pip resolves the remaining detected findings. Exact scan
evidence and limits: [STABLE-ACCEPTANCE.md](STABLE-ACCEPTANCE.md).

## Publication

Release runs only after all required checks pass on the main merge commit.
The published tag, source assets, checksums, and workflow results are verified
against the reviewed source revision. See [RELEASE.md](RELEASE.md) and
[INSTALL.md](INSTALL.md) for reproducible commands.
