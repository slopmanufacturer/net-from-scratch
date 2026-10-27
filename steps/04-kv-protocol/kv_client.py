#!/usr/bin/env python3
"""Step 04: a tiny client for the key-value server."""

import argparse
import socket
import sys

parser = argparse.ArgumentParser()
parser.add_argument("port", nargs="?", type=int, default=8000)
parser.add_argument("--host", default="127.0.0.1")
args = parser.parse_args()

with socket.create_connection((args.host, args.port)) as sock:
    reader = sock.makefile("r")
    print("commands: SET key value | GET key | DEL key | QUIT")
    for line in sys.stdin:
        sock.sendall(line.encode())
        print(reader.readline(), end="")
        if line.strip().upper() == "QUIT":
            break
