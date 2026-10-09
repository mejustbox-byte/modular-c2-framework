# Stable source promotion acceptance — 2026-10-09

Scope: one synthetic mock agent only. Stable source release `v0.1.0` is published.
GitHub release and tag were independently read back and match the tested SHA.

## Runtime and containment

Python pin and minimum version: 3.12.15; no application package dependencies.
Official base: `python:3.12.15-alpine3.24` with manifest digest
`sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4`.
Pin patched zlib `1.3.2-r1`; remove unused runtime pip/ensurepip.
Non-root, read-only root, no capabilities/new privileges, bounded tmpfs/resources,
no host mounts, no published ports, no external network. Docker inspection occurs
before the listener; application runtime verifies OS controls independently.

## Observed evidence

Initial runtime/browser/CVE gate run:
[37893829054](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37893829054),
source `8952adfb6de0d88b38224803f948de2f40d1d9b9`: smoke, container and image-audit
passed. Real Firefox rendered and exercised viewer/operator/admin UI, status,
audit and role management. Absent client identity and untrusted server CA were
refused with HTTPS validation enabled. Desktop screenshots were inspected.
This first Alpine scan had no HIGH/CRITICAL but 6 MEDIUM and 1 LOW findings.

Follow-up dependency-remediation source:
`7cbfbb695a46af56c0deae8ab816f314361a6910`, run
[37894124919](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37894124919).
The full Trivy JSON was downloaded, its artifact digest verified and all
severity counts inspected: **0 detected CVEs** across 38 Alpine packages.
Application image ID:
`sha256:9091afe786ab8bb503f6a52149565b49a1941a479962bccb7ac44891aec289b0`.
Audit/SBOM artifact SHA256:
`b5e7adb68b60fc1e4ab1095895034804ae861674f91bd24fb94ce80ce4b13cd9`.
Enhanced Firefox probes initially failed with concurrent process trees under
the bounded test container. Sequential probes now pass, including actual
HTTP 403 on revoked identities and renewed role-specific UI after regrant.

Final stable-metadata source:
`a327beb5727294e18ef60c00b50b7311f770b6b0`, run
[37894625963](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37894625963):
**smoke, container/browser and image-audit all passed**. This includes 34 unit
tests, five contained integration tests, real mTLS-negative cases, all three
roles and fresh-session operator/revoked/viewer transitions. Main merge gates
will run the same checks again before publication.


The initial Bookworm image was rejected with 53 HIGH and 2 CRITICAL findings;
none were suppressed. The later image patches also resolved every detected
MEDIUM/LOW finding by updating zlib and removing the unused package installer.

## Reproducible checks

- Python 3.12.15: 34 unit/negative/CLI/API/recovery/publication tests; 4 smoke checks.
- Ruff 0.16.10 lint/format; shell syntax; whitespace and required document links.
- Five contained API/egress/lifecycle/audit/restart/cleanup tests.
- Real Firefox, Playwright 1.63.0, native NSS CA and client identities; no TLS bypass.
- Trivy 0.75.0 checksum-pinned binary; complete CVE JSON and CycloneDX SBOM.
- Exact main merge SHA is tested again by all three jobs before stable publication.

Artifacts contain synthetic screenshots and package reports only; no test PKI,
journals, tokens or browser profiles are exported. Reports remain workflow artifacts
with 14-day screenshot and 30-day audit retention. This repository report preserves
the acceptance summary and provenance after their expiration.

## Limits

CVE results are a point-in-time database scan of the shipped application image;
unknown vulnerabilities and separate CI/browser tool images are outside that claim.
Real headless Firefox acceptance does not verify every browser/OS or a user's VM.
The independently published/restored Cloud snapshot remains historical rc.1 with
Python 3.12.14; current runtime evidence is local and CI, not a new Cloud restoration.
Cloud runtime containment is unverified and no lab listener runs there.
No public deployment, real agent or arbitrary command capability is included.

## Published release and final main evidence

[Stable v0.1.0](https://github.com/mejustbox-byte/modular-c2-framework/releases/tag/v0.1.0) published at `2026-10-09T06:47:33Z`.
Both release target and Git tag point to tested main merge commit
`b52f84446734a1a5512d8f4db9ea13445ae8a388`. API confirms `draft=false`, `prerelease=false`.

[Main release CI](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37895275757):
smoke, container/browser, image-audit and stable publication all completed success.
Full final main audit artifact was downloaded and digest verified. Its JSON
contains **0 detected CVEs at every severity** across 38 Alpine 3.24.2 packages.
Image ID: `sha256:767a01637331f2a0468a3c71c27500596ced83a0f8533618cb82e424affbe6bc`.
Audit/SBOM artifact SHA256: `719868e4d625bcf80dc84e03a733e2b10bdfc35259909d757019bf2c6e3ca98c`.

- [browser-acceptance](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37895275757/artifacts/11600156632): `sha256:52820363bc57255c005f2e6acb1490c07acd90944a08ae395e606b28c8112bff`.
- [image-security-audit](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37895275757/artifacts/11599069467): `sha256:719868e4d625bcf80dc84e03a733e2b10bdfc35259909d757019bf2c6e3ca98c`.

This publication does not change the historical Cloud snapshot or enable public hosting.
