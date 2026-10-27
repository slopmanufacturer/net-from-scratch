#!/usr/bin/env python3
"""Step 10: decode a chunked response by hand."""

import argparse
import socket

parser = argparse.ArgumentParser()
parser.add_argument("port", nargs="?", type=int, default=8000)
parser.add_argument("--host", default="127.0.0.1")
args = parser.parse_args()

with socket.create_connection((args.host, args.port)) as sock:
    sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
    reader = sock.makefile("rb")

    while True:
        line = reader.readline()
        if line in (b"\r\n", b"\n", b""):
            break
        print(line.decode().strip())

    body = b""
    while True:
        size = int(reader.readline().split(b";")[0].strip(), 16)
        if size == 0:
            reader.readline()
            break
        body += reader.read(size)
        reader.read(2)

    print("body:", body.decode(), end="")
