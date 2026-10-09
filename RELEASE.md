# Source release v0.1.0

Stable source release of the bounded, one-agent educational mock laboratory.
Python metadata is `0.1.0`; intended tag is `v0.1.0`. The GitHub Releases page
is authoritative for publication status and exact commit. No package upload,
public server, registry publication or production deployment is included.
The MIT license and original attribution remain unchanged.

## Included

Synthetic ping/status/emit_test_event/stop, strict envelopes, offline CLI,
loopback TLS 1.3/mTLS API, static UI, server-side roles/revocation, bounded
SQLite audit/restart recovery and verified container containment.
Python 3.12.15, digest-pinned Alpine 3.24 runtime and patched zlib 1.3.2-r1;
unused pip and ensurepip are removed from the application image.

## Acceptance and publication

34 unit tests, 4 smoke checks, Ruff lint/format, five contained integration
tests, real Firefox native NSS mTLS UI acceptance and full image CVE/SBOM
auditing are mandatory. Evidence: [VALIDATION.md](VALIDATION.md) and
[STABLE-ACCEPTANCE.md](STABLE-ACCEPTANCE.md). Browser tests cover all roles,
audit, role changes/revocation and refusal without identity or a trusted CA.
The scanner fails on every HIGH/CRITICAL finding without suppressions.

A main merge title beginning `Release v` activates publication only after
smoke, container/browser and image-audit jobs succeed on the exact merge SHA.
Only publication receives contents-write permission; the ephemeral Actions
token is neither logged nor saved. Four mocked publication tests verify
main-only execution, exact-commit stable creation, idempotency and refusal to
overwrite another source commit. Failed checks leave the release unpublished.

GitHub supplies source archives. Obtain the release from
[GitHub Releases](https://github.com/mejustbox-byte/modular-c2-framework/releases)
and follow [INSTALL.md](INSTALL.md). Re-run an actual failed workflow after a
reviewed fix; never bypass TLS, containment or image audit to publish.

## Scope and limits

Browser acceptance uses real headless Firefox in the same isolated lab network
namespace, trusted synthetic CA and native client certificate selection. It
does not attest every browser/OS or a user's separate VM. CVE results are a
point-in-time scan against the fetched database, not proof against unknown flaws.
The browser/tool image is CI-only; the full image audit covers the shipped
application runtime. Ordinary Cloud/host workspaces remain unverified runtime
containment: no laboratory listener is allowed there. The published Cloud
snapshot was independently checked for rc.1/Python 3.12.14, not this version.

Stable refers to the documented synthetic mock MVP; production C2, real agents,
arbitrary execution, persistence, stealth and public hosting remain excluded.

## Rollback

Acceptance cleanup stops and removes only its disposable containers and PKI.
Retained offline journals are not reset: preserve them for review and create a
new private directory for another exercise. Source rollback uses a reviewed
revert PR, without rewriting shared history.
