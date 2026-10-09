"""Linux runtime guard. External Docker inspection is also required."""

import os
from pathlib import Path

from .core import LabError


def verify():
    try:
        if os.getuid() == 0:
            raise LabError("containment_required")
        interfaces = {p.name for p in Path("/sys/class/net").iterdir()}
        if interfaces != {"lo"}:
            raise LabError("containment_required")
        for line in Path("/proc/net/route").read_text().splitlines()[1:]:
            if line.split()[0] != "lo":
                raise LabError("containment_required")
        for line in Path("/proc/net/ipv6_route").read_text().splitlines():
            if line.split()[-1] != "lo":
                raise LabError("containment_required")
        status = dict(
            line.split(":", 1)
            for line in Path("/proc/self/status").read_text().splitlines()
            if ":" in line
        )
        if int(status["CapEff"].strip(), 16) != 0 or status["NoNewPrivs"].strip() != "1":
            raise LabError("containment_required")
        mounts = [line.split() for line in Path("/proc/self/mountinfo").read_text().splitlines()]
        if not any(row[4] == "/" and "ro" in row[5].split(",") for row in mounts):
            raise LabError("containment_required")
        if Path("/var/run/docker.sock").exists():
            raise LabError("containment_required")
    except (OSError, ValueError, KeyError, IndexError):
        raise LabError("containment_required") from None
