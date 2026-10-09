"""Verify Docker inspection before starting any laboratory listener."""

import json
import sys

container = json.load(sys.stdin)[0]
host, config = container["HostConfig"], container["Config"]
checks = [
    host["NetworkMode"] == "none",
    host["ReadonlyRootfs"],
    not host["Privileged"],
    host.get("CapDrop") == ["ALL"],
    not host.get("CapAdd"),
    "no-new-privileges" in (host.get("SecurityOpt") or []),
    not host.get("PortBindings"),
    not host.get("Binds"),
    config["User"] == "10001:10001",
    host["Memory"] > 0,
    host["NanoCpus"] > 0,
    host["PidsLimit"] > 0,
    not container.get("Mounts"),
    set(host.get("Tmpfs", {})) == {"/run/lab"},
]
if not all(checks):
    raise SystemExit("Container configuration refused")
print("Container configuration verified: isolated, private, non-root, bounded.")
