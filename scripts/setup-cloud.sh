#!/usr/bin/env bash
# Run from a clean checkout with the pinned project toolchain available.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
cd -- "$script_dir/.."
bash scripts/check-workspace.sh
if [[ "$(uv --version)" != 'uv 0.12.24'* ]]; then
  printf '%s\n' 'ERROR: install the pinned uv 0.12.24 from the official package registry.' >&2
  exit 1
fi
uv sync --locked
uv run --locked --offline python scripts/smoke.py
uv run --locked --offline python -m unittest discover -s tests -v
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
