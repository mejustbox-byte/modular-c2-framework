# Stable Acceptance

This document defines the product checks required before a stable release.

## Automated checks

- Locked dependency installation succeeds from a clean checkout.
- Unit, CLI, lint, formatting, and documentation checks pass in CI.
- Container acceptance verifies the configured non-root, read-only, resource,
  capability, and network restrictions.
- Browser tests exercise mTLS, role boundaries, session expiry, and negative
  certificate cases in an isolated test namespace.
- The published source artifact matches the reviewed release commit.

## Release boundaries

The repository implements a controlled mock laboratory. It does not include a
production command-and-control service, arbitrary command execution, real agent
deployment, public hosting, or persistence on target systems. CI and synthetic
tests do not establish security of a production host. Run operational and
containment checks on a separate authorized laboratory before any deployment.
