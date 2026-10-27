#!/usr/bin/env python3
"""Step 01: type lines here, the server sends them straight back."""

import argparse
import socket
import sys

parser = argparse.ArgumentParser()
parser.add_argument("port", nargs="?", type=int, default=8000)
parser.add_argument("--host", default="127.0.0.1")
args = parser.parse_args()

with socket.create_connection((args.host, args.port)) as sock:
    print(f"connected to {args.host}:{args.port}, ctrl-d to quit")
    for line in sys.stdin:
        sock.sendall(line.encode())
        print(sock.recv(1024).decode(), end="")
