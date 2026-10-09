#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
fixture_parent="$(mktemp -d)"
container_id=''
cleanup() {
  if [[ -n "$container_id" ]]; then docker rm -f "$container_id" >/dev/null; fi
  # Remove only this script's disposable synthetic certificate directory.
  sudo rm -rf -- "$fixture_parent"
}
trap cleanup EXIT
python3 scripts/make-lab-fixture.py "$fixture_parent/pki"
docker version --format 'Docker Engine {{.Server.Version}}'
docker build -t modular-c2-lab:ci .
container_id="$(docker run -d --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --user 10001:10001 --memory 256m --cpus 1 \
  --pids-limit 64 --tmpfs /run/lab:rw,noexec,nosuid,nodev,mode=0700,uid=10001,gid=10001,size=32m \
  modular-c2-lab:ci python -c 'import time; time.sleep(600)')"
docker inspect "$container_id" | python3 scripts/check-container.py
sudo chown -R 10001:10001 "$fixture_parent/pki"
sudo tar -C "$fixture_parent/pki" -cf - \
  ca.crt server.crt server.key viewer.crt viewer.key operator.crt operator.key \
  admin.crt admin.key principals.json | docker exec -i "$container_id" \
  tar -C /run/lab --no-same-owner -xf -
docker exec "$container_id" python -m unittest discover -s integration -v
printf '%s\n' 'Contained integration, mTLS, lifecycle, audit and egress checks passed.'
