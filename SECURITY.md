# Security Policy

Authorized isolated educational exercises only. The only agent is synthetic,
with ping/status/emit_test_event/stop. No arbitrary commands, host reconnaissance,
stealth, persistence, defense bypass or third-party targets.

## Enforced controls

- Loopback only; TLS 1.3; mandatory verified/pinned client certificates.
- Server-side role and lab boundaries, expiry, revocation and replay protection.
- Strict bounded messages, request budget, one agent and bounded audit/recovery.
- Startup/request guard refuses root, active capabilities, missing no-new-privileges,
  writable root or non-loopback interfaces/routes.
- Official Docker image pinned by digest, network none, no ports/binds, private tmpfs,
  memory/CPU/PID limits; external inspect validation precedes acceptance.
- Fixed UI asset table, no traversal/credential storage/CORS; Host/Origin checks,
  CSP, no-store and generic diagnostics.

Loopback alone is not containment. Runtime guard cannot attest host mounts or a
malicious OS owner; trusted external Docker inspection and controlled-lab ownership
are required. Certificate authority administration is trusted. Do not bypass guards,
TLS verification or private storage permissions. An arbitrary local Python caller
is outside the remote authorization boundary and may alter internal objects.

## Public OPSEC

Only synthetic fixtures and disposable one-day test PKI. Never commit tokens,
certificates/private keys, production logs, internal hostnames or target inventories.
PKI is created outside checkout/image; CI deletes its own disposable data.
Platform-managed credentials are not copied to project files or diagnostics.
Project Cloud environment contains no project/network secrets; its independent
containment remains unverified, so network laboratory services must not run there.

The accidental-secret scanner is limited signatures, not a full secrets audit.
Audit read/authentication rejection at TLS boundary is not a durable security log.
Do not claim production security, tamper-proof auditing or protection from OS admin.

## Vulnerability reporting

Use GitHub private Security Advisories. Do not publish weaponized payloads, live
infrastructure or secrets in issues. If private reporting is unavailable, obtain
an appropriate private reporting channel first. Revoke/rotate exposed credentials;
a later deletion does not erase Git history. Stop/isolate the lab, preserve sanitized
evidence and review incomplete journal operations before resuming.
