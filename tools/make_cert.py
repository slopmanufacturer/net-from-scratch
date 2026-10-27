#!/usr/bin/env python3
"""Create a throwaway CA and a localhost certificate under .certs/ with openssl.

Chapters 17-20 use these. Nothing here is secret: the keys live next to the
code and are meant to be thrown away.
"""

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CERTS = ROOT / ".certs"


def openssl(*args):
    subprocess.run(
        ["openssl", *args],
        check=True,
        cwd=CERTS,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def ensure(force=False):
    if not shutil.which("openssl"):
        print("openssl not found, skipping the TLS chapters")
        return False
    CERTS.mkdir(exist_ok=True)
    if (CERTS / "server.pem").exists() and not force:
        return True

    (CERTS / "san.cnf").write_text(
        "basicConstraints = CA:FALSE\n"
        "keyUsage = digitalSignature, keyEncipherment\n"
        "extendedKeyUsage = serverAuth\n"
        "subjectAltName = DNS:localhost, IP:127.0.0.1\n"
    )
    openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "3650",
            "-keyout", "ca.key", "-out", "ca.pem",
            "-subj", "/CN=net-from-scratch CA",
            "-addext", "basicConstraints=critical,CA:TRUE",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign")
    openssl("req", "-newkey", "rsa:2048", "-nodes", "-keyout", "server.key",
            "-out", "server.csr", "-subj", "/CN=localhost")
    openssl("x509", "-req", "-in", "server.csr", "-CA", "ca.pem", "-CAkey", "ca.key",
            "-CAcreateserial", "-out", "server.pem", "-days", "3650",
            "-extfile", "san.cnf")
    print(f"wrote {CERTS.relative_to(ROOT)}/ (ca.pem, server.pem, server.key)")
    return True


if __name__ == "__main__":
    sys.exit(0 if ensure("--force" in sys.argv) else 1)
