#!/usr/bin/env python3
"""Step 19: look at the certificate the server actually presented."""

import argparse
import pathlib
import socket
import ssl
import sys

CERTS = pathlib.Path(__file__).resolve().parents[2] / ".certs"

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost")
parser.add_argument("--port", type=int, default=8443)
parser.add_argument("--cafile", default=str(CERTS / "ca.pem"))
args = parser.parse_args()

if not pathlib.Path(args.cafile).exists():
    sys.exit("run `python tools/make_cert.py` first")

context = ssl.create_default_context(cafile=args.cafile)

with socket.create_connection((args.host, args.port), timeout=5) as sock:
    with context.wrap_socket(sock, server_hostname=args.host) as tls:
        cert = tls.getpeercert()

print("subject:")
for key, value in cert["subject"][0]:
    print(f"  {key}: {value}")

print("issuer:")
for key, value in cert["issuer"][0]:
    print(f"  {key}: {value}")

print("subjectAltName:")
for kind, value in cert.get("subjectAltName", ()):
    print(f"  {kind}: {value}")

print(f"valid from: {cert['notBefore']}")
print(f"valid to:   {cert['notAfter']}")
print(f"serial:     {cert['serialNumber']}")
