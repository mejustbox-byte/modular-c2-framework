#!/usr/bin/env bash
# Read-only setup check; no downloads, credentials, or service startup.
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(git -C "$script_dir/.." rev-parse --show-toplevel)"
cd -- "$repo_root"

origin="$(git remote get-url origin)"
case "$origin" in
  https://github.com/mejustbox-byte/modular-c2-framework|\
  https://github.com/mejustbox-byte/modular-c2-framework.git|\
  git@github.com:mejustbox-byte/modular-c2-framework.git|\
  ssh://git@github.com/mejustbox-byte/modular-c2-framework.git) ;;
  *) printf '%s\n' 'ERROR: origin is not the authorized repository.' >&2; exit 1 ;;
esac

for document in README.md ROADMAP.md INSTALL.md CHANGELOG.md LICENSE SECURITY.md AGENTS.md ARCHITECTURE.md THREAT-MODEL.md CONTRIBUTING.md TECH-STACK.md; do
  if [[ ! -s "$document" ]]; then
    printf 'ERROR: required document is missing or empty: %s\n' "$document" >&2
    exit 1
  fi
done

git diff --check
git diff --cached --check
printf '%s\n' 'Workspace check passed: authorized repository and required documents.'
printf 'Branch: %s\n' "$(git branch --show-current)"
git status --short
