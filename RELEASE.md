# Release candidate v0.1.0-rc.1

First source-only prerelease of the bounded educational mock laboratory.
Python metadata is `0.1.0rc1`; GitHub tag is `v0.1.0-rc.1`. No PyPI upload,
public server, container registry publication or production deployment is included.
The MIT license and original attribution remain unchanged.

## Included

One synthetic agent with ping/status/emit_test_event/stop, strict envelopes,
offline CLI, loopback TLS 1.3/mTLS API, local static UI, server-side roles and
revocation, bounded SQLite audit and restart recovery, containment guards,
digest-pinned Docker acceptance and reproducible development checks.

## Acceptance and publication

30 unit tests, 4 smoke checks, lint/format and five contained integration tests
passed on the implementation commit; evidence is in [VALIDATION.md](VALIDATION.md).
Three additional mocked publication tests cover main-only execution, exact-commit
prerelease creation and refusal to overwrite another source commit.
The final main merge commit is tested again before publication. A release merge
title beginning `Release v` activates the release job; it depends on successful
smoke and container jobs and publishes a prerelease targeting that exact SHA.
Only this job receives contents-write permission. It uses the ephemeral Actions
token without logging or saving it. No additional project secret is required.

Source archives are supplied by GitHub. Obtain the version from
[GitHub Releases](https://github.com/mejustbox-byte/modular-c2-framework/releases)
and follow [INSTALL.md](INSTALL.md). A failed release job leaves the candidate
unpublished; fix the failure and rerun the workflow, never bypass its checks.

## Remaining operational acceptance

- Full visual interaction using a same-namespace browser, trusted lab CA and
  enrolled client certificate has not been verified. HTTP assets and API are tested.
- The release revision passed repeated setup in the existing Codex Cloud environment
  after a verified local bundle import. Updated publication/restoration evidence is
  recorded in [ACCEPTANCE-2026-10-09.md](ACCEPTANCE-2026-10-09.md).
- Ordinary Cloud/host workspaces are not verified runtime containment. They may
  run offline development checks; network listeners must refuse those environments.
- Python 3.12.14 is the tested baseline, not a claim of the latest security patch.
  Review runtime/tool advisories before stable promotion or expanded deployment.

These limitations keep this release a candidate. Stable promotion requires recorded
operational evidence, review of current runtime advisories and a new versioned
release. Never expose the container port or disable mTLS/containment to test the UI.

## Rollback

Stop the disposable lab and remove only its own runtime/container data using the
acceptance script cleanup. Retained offline journals are not automatically reset:
preserve them for review and create a new private directory for a new exercise.
To reverse a source change, use a reviewed revert PR; do not rewrite shared history.
