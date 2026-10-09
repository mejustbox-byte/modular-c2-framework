# Repository instructions

## Scope

- Work only in `mejustbox-byte/modular-c2-framework`.
- Before edits, inspect `git status --short`, the current branch, and relevant files.
- Follow applicable instructions in parent and nested `AGENTS.md` files.
- Do not read `CLAUDE.md` unless a specific task makes it necessary.
- Preserve existing files; do not delete files or overwrite unrelated work.
- Use a task branch and a reviewable pull request. Never force-push.

## Public development and OPSEC

This repository is a controlled-lab educational platform using mock agents.
Public examples must use synthetic data, placeholder identities and test keys.
Do not commit credentials, production telemetry, real target details, internal
addresses, or operational infrastructure. Keep authentication material out of
terminal output, documents, and public issues.

For future laboratory components, preserve the documented loopback-only,
restricted-command and audit requirements. Network isolation must be enforced
by the laboratory environment and verified, not assumed from a bind address.
Stealth, persistence, defense bypass and unrestricted command execution are
outside the project's documented MVP scope.

## Documentation

Maintain `README.md`, `ROADMAP.md`, `INSTALL.md`, `CHANGELOG.md`, `LICENSE`, and
`SECURITY.md` as the implementation evolves. Distinguish planned capabilities
from implemented behavior. Preserve the MIT license and copyright attribution.
Record material changes under `Unreleased`; do not invent releases or dates.

## Verification

Run `bash scripts/check-workspace.sh` from the repository root before and after
changes. Run feature-specific checks once code exists. Report commands, results,
and any checks that could not run. Do not claim Codex Cloud was connected or
published without observing that state in the product.
