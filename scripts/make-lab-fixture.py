"""Disposable synthetic PKI only. Never print keys, certificates or credentials."""

import hashlib
import json
import os
import ssl
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
root.mkdir(mode=0o700, parents=True, exist_ok=False)
os.umask(0o077)


def openssl(*args):
    subprocess.run(["openssl", *args], cwd=root, check=True, capture_output=True, timeout=30)


openssl(
    "req",
    "-x509",
    "-newkey",
    "rsa:2048",
    "-nodes",
    "-days",
    "1",
    "-subj",
    "/CN=Synthetic Lab CA",
    "-keyout",
    "ca.key",
    "-out",
    "ca.crt",
)
principals = []
for name in ("server", "viewer", "operator", "admin"):
    openssl(
        "req",
        "-newkey",
        "rsa:2048",
        "-nodes",
        "-subj",
        f"/CN={name}",
        "-keyout",
        f"{name}.key",
        "-out",
        f"{name}.csr",
    )
    extension = (
        "subjectAltName=IP:127.0.0.1\nextendedKeyUsage=serverAuth\n"
        if name == "server"
        else "extendedKeyUsage=clientAuth\n"
    )
    (root / f"{name}.ext").write_text(extension)
    openssl(
        "x509",
        "-req",
        "-in",
        f"{name}.csr",
        "-CA",
        "ca.crt",
        "-CAkey",
        "ca.key",
        "-CAcreateserial",
        "-days",
        "1",
        "-extfile",
        f"{name}.ext",
        "-out",
        f"{name}.crt",
    )
    if name != "server":
        der = ssl.PEM_cert_to_DER_cert((root / f"{name}.crt").read_text())
        principals.append(
            {
                "actor": name,
                "role": "lab-admin" if name == "admin" else name,
                "fingerprint": hashlib.sha256(der).hexdigest(),
            }
        )
(root / "principals.json").write_text(
    json.dumps({"lab_id": "synthetic-lab", "principals": principals})
)
print("Synthetic one-day PKI fixture prepared in the requested private directory.")
