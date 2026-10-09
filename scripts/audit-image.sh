#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p reports
scanner_dir="$(mktemp -d)"
trap 'rm -rf -- "$scanner_dir"' EXIT
curl --fail --location --retry 3 --output "$scanner_dir/trivy.tar.gz" \
  https://github.com/aquasecurity/trivy/releases/download/v0.75.0/trivy_0.75.0_Linux-64bit.tar.gz
printf '%s  %s\n' c6e65abddb348e25f10549df887045629cf28cc72453cd1c63acb717316b3f3f \
  "$scanner_dir/trivy.tar.gz" | sha256sum --check --strict
tar -xzf "$scanner_dir/trivy.tar.gz" -C "$scanner_dir" trivy
"$scanner_dir/trivy" --version
docker build -t modular-c2-lab:ci .
"$scanner_dir/trivy" image --scanners vuln --format json --output reports/image-cve.json modular-c2-lab:ci
"$scanner_dir/trivy" image --format cyclonedx --output reports/image-sbom.cdx.json modular-c2-lab:ci
# No ignored findings or ignore-unfixed: every known HIGH/CRITICAL blocks promotion.
"$scanner_dir/trivy" image --scanners vuln --severity HIGH,CRITICAL --exit-code 1 modular-c2-lab:ci
