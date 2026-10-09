# Acceptance report — 2026-10-09

Source under test: release `v0.1.0-rc.1`, commit
`c27150a2c0fa3280208f0efe8afa9adb3178a4da`, tree
`5b656b9cdf72026f872847d168a1cad6d19a76ce`.
The release tag was read back and points to this commit. GitHub reports a published
prerelease, not a draft. Source trees in local verification and GitHub match.

## Repeated checks

| Check | Result | Evidence / limit |
| --- | --- | --- |
| Workspace and Git diff | Passed | Authorized origin, required docs, clean source checkout |
| Unit/negative/CLI/API/recovery/release tests | Passed, 33 | `python3 -m unittest discover -s tests -v` |
| Smoke and common accidental-secret signatures | Passed, 4 | `python3 scripts/smoke.py`; limited signatures |
| Released Git ancestry signatures | Passed, 115 unique blobs | Same four signature classes, no raw content printed; limited scan |
| Ruff lint/format | Passed | Ruff 0.16.10; 32 Python files |
| Locked offline dependency sync | Passed | `uv sync --locked --offline`; CI uses pinned uv 0.12.24 |
| Shell and JavaScript syntax | Passed | `bash -n` for all three shell scripts; `node --check mocklab/web/app.js` |
| Offline demo and interactive menu | Passed | CLI fixed lifecycle, audit display and identity revocation |
| Startup outside containment | Passed refusal | `python3 -m mocklab.server` exits 1 with fixed refusal; no listener starts |
| Main-commit container acceptance | Passed, 5 | mTLS, HTTP assets, RBAC, scope/replay, membership/revocation, lifecycle/audit/restart and cleanup |
| Main-commit publication | Passed | Source prerelease targets exact tested commit |

Main-commit smoke/container/release evidence:
[Actions run 37889473519](https://github.com/mejustbox-byte/modular-c2-framework/actions/runs/37889473519).

Additional local execution of the packaged JavaScript in a mocked DOM covered
viewer button restrictions, safe text audit display, operator fixture envelopes,
admin revocation payloads and disabled controls after failed authentication.
All five behavior groups passed. This temporary in-process test has no browser,
TLS, CSS/layout or network coverage and does not complete visual UI acceptance.

## Cloud verification

The previous published environment still held the setup-only PR #1 commit. Its
two-domain policy refused GitHub refresh (CONNECT 403). A verified local Git bundle
was uploaded and imported without expanding internet access or adding credentials.

Bundle SHA-256:
`aec881c5b1cace1312d85265e20d13bce497201037dec4a28cde977511511c43`.
Both prerequisite commits and the exact release HEAD/tree were verified. The old
checkout was retained as a branch. On the exact release commit, repeated Cloud setup
passed 33/33 unit tests, 4/4 smoke, Ruff lint/format for 32 files, the CLI demo and
expected server refusal (exit 1). Install/start fields were replaced and read back
with the new HEAD/tree pin. UI showed Only me, two custom domains, no network
secrets and no configured environment variables. UI publication completed and showed Environment published. Independent restoration
passed in a new task from this published environment: exact HEAD/tree, Python/uv/Ruff
versions, locked offline sync, 33 unit tests, 4 smoke, lint/format, CLI demo, shell
syntax and expected server refusal. Git remained clean. An in-process Python audit
hook observed zero socket creation/bind during refused startup; ptrace/strace was
unavailable and is not claimed.

A direct sync initially encountered the default read-only cache. The exact saved
startup was then independently rerun with `UV_CACHE_DIR=/workspace/.cache/modular-c2-uv`,
`UV_OFFLINE=1` and `UV_PYTHON_DOWNLOADS=never`: exit 0, all checks passed, no packages
installed/downloaded, unchanged HEAD/tree and clean Git before/after.

Runtime inspector reported configured domains pypi.org/files.pythonhosted.org, no
presets, and effective alias www.pypi.org. Enforcement state remained unknown. This
does not attest runtime containment or OS-level egress denial; network services
remain prohibited in Cloud.

## Runtime and advisory review

The pinned baseline remains Python 3.12.14. The official
[Python 3.12.15 release notes](https://www.python.org/downloads/release/python-31215/)
identify a newer security release dated 2026-09-30. Runtime patch adoption and
revalidation remain required before stable promotion; candidate acceptance does
not certify the older baseline as fully patched.

The three newest published uv advisories inspected have patched versions at or
below pinned uv 0.12.24: [Windows wheel traversal](https://github.com/astral-sh/uv/security/advisories/GHSA-2cv4-cqwr-gwf7),
[entry-point writes](https://github.com/astral-sh/uv/security/advisories/GHSA-4gg8-gxpx-9rph),
and [RECORD deletion](https://github.com/astral-sh/uv/security/advisories/GHSA-pjjw-68hj-v9mw).
The [Ruff maintainer security page](https://github.com/astral-sh/ruff/security)
reported no published advisories when reviewed. These observations are bounded
manual reviews, not a complete vulnerability scan or absence-of-vulnerabilities proof.
No full container OS/package CVE scan or SBOM audit was performed.

## Outstanding acceptance

Full visual interaction and client-certificate selection in a real browser sharing
a verified isolated namespace remain untested. No such VM/browser is connected to
this session; the available cloud browser is outside the laboratory namespace.
The [Cloud product documentation](https://learn.chatgpt.com/docs/environments/cloud-environments)
also documents browser/computer use as unsupported in its coding environment. A host port exposure or TLS/containment bypass is not an acceptance method.

The project remains a source release candidate until browser acceptance and runtime
patch revalidation are recorded. No stable release or public deployment is claimed.
