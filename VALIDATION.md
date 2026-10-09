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

## Publication and Cloud scope

Release runs only after all three jobs pass again on the main merge commit.
The v0.1.0 tag and published stable release were read back and match tested
main SHA `b52f84446734a1a5512d8f4db9ea13445ae8a388`. All four main jobs completed success:
[37895275757](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37895275757). Source/installation:
[RELEASE.md](RELEASE.md), [INSTALL.md](INSTALL.md).

Cloud remains a development-only workspace with runtime containment unverified;
no listener runs there. Its independently restored published snapshot was rc.1,
Python 3.12.14. Historical evidence: [ACCEPTANCE-2026-10-09.md](ACCEPTANCE-2026-10-09.md).
These old results do not claim current Cloud restoration. Browser and CVE
acceptance now run separately in CI, without expanding the Cloud allowlist.
