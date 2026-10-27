#!/usr/bin/env python3
"""Step 18: fetch a page over TLS and show the status and body."""

import argparse
import pathlib
import socket
import ssl
import sys

CERTS = pathlib.Path(__file__).resolve().parents[2] / ".certs"

parser = argparse.ArgumentParser()
parser.add_argument("path", nargs="?", default="/")
parser.add_argument("port", nargs="?", type=int, default=8443)
parser.add_argument("--host", default="localhost")
parser.add_argument("--cafile", default=str(CERTS / "ca.pem"))
parser.add_argument("--insecure", action="store_true", help="skip certificate checks")
args = parser.parse_args()

if args.insecure:
    context = ssl._create_unverified_context()
else:
    if not pathlib.Path(args.cafile).exists():
        sys.exit("run `python tools/make_cert.py` first, or pass --insecure")
    context = ssl.create_default_context(cafile=args.cafile)

with socket.create_connection((args.host, args.port), timeout=5) as sock:
    with context.wrap_socket(sock, server_hostname=args.host) as tls:
        tls.sendall(f"GET {args.path} HTTP/1.1\r\nHost: {args.host}\r\n\r\n".encode())
        data = b""
        while True:
            chunk = tls.recv(4096)
            if not chunk:
                break
            data += chunk

head, _, body = data.partition(b"\r\n\r\n")
print(head.decode("latin-1").split("\r\n")[0])
print(f"{len(body)} bytes of body")
print(body.decode("utf-8", "replace")[:200])
