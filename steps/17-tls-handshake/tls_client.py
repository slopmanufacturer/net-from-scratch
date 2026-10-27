#!/usr/bin/env python3
"""Step 17: connect with verification on, then say what was negotiated."""

import argparse
import pathlib
import socket
import ssl
import sys

CERTS = pathlib.Path(__file__).resolve().parents[2] / ".certs"

parser = argparse.ArgumentParser()
parser.add_argument("port", nargs="?", type=int, default=8443)
parser.add_argument("--host", default="localhost")
parser.add_argument("--cafile", default=str(CERTS / "ca.pem"))
args = parser.parse_args()

if not pathlib.Path(args.cafile).exists():
    sys.exit("run `python tools/make_cert.py` first")

context = ssl.create_default_context(cafile=args.cafile)

with socket.create_connection((args.host, args.port), timeout=5) as sock:
    with context.wrap_socket(sock, server_hostname=args.host) as tls:
        print("version:", tls.version())
        print("cipher: ", tls.cipher()[0])
        print("peer:   ", tls.getpeercert()["subject"])

        tls.sendall(b"hello over tls\n")
        print("echo:   ", tls.recv(1024).decode().strip())
