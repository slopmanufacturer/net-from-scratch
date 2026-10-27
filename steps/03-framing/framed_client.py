#!/usr/bin/env python3
"""Step 03: read three framed messages, then send two in a single write."""

import argparse
import socket
import sys

from framed_server import recv_message, send_message

parser = argparse.ArgumentParser()
parser.add_argument("port", nargs="?", type=int, default=8000)
parser.add_argument("--host", default="127.0.0.1")
args = parser.parse_args()

with socket.create_connection((args.host, args.port)) as sock:
    for _ in range(3):
        print("server:", recv_message(sock).decode())

    blob = b""
    for message in (b"one", b"two"):
        blob += len(message).to_bytes(4, "big") + message
    sock.sendall(blob)

    print("echo:", recv_message(sock).decode(), recv_message(sock).decode())
