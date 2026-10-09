# Stable source promotion acceptance — 2026-10-09

Scope: one synthetic mock agent only. Source metadata `0.1.0` is prepared for
stable publication; GitHub Releases is authoritative for the published tag/SHA.

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

## Publication

Publication has not yet been claimed in this report. A main merge title beginning
`Release v` runs the stable-release job only after smoke, container/browser and
image-audit success. The release notes append the exact tested SHA and CI URL.
The release/tag must then be read back before reporting publication complete.
