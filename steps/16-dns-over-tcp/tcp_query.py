#!/usr/bin/env python3
"""Step 16: query the stub resolver over TCP instead of UDP."""

import argparse
import pathlib
import random
import socket
import sys

STEPS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STEPS / "14-dns-query"))
from dns_query import build_query, parse_response


def recv_exactly(sock, size):
    buf = b""
    while len(buf) < size:
        chunk = sock.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("peer closed")
        buf += chunk
    return buf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--server", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5353)
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()

    qid = random.randrange(0, 65536)
    query = build_query(args.name, qid)

    with socket.create_connection((args.server, args.port), timeout=args.timeout) as sock:
        sock.sendall(len(query).to_bytes(2, "big") + query)
        size = int.from_bytes(recv_exactly(sock, 2), "big")
        response = recv_exactly(sock, size)

    got_id, rcode, answers = parse_response(response)
    if got_id != qid:
        print(f"response id {got_id} does not match query id {qid}")
        return 1
    if rcode != 0:
        print(f"{args.name}  rcode {rcode}")
        return 1

    for name, _, ttl, value in answers:
        print(f"{name}  {ttl}s  A  {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
