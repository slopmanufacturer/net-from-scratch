#!/usr/bin/env python3
"""Step 16: the same DNS message, with a two-byte length in front, over TCP."""

import argparse
import pathlib
import socket
import sys
import threading

STEPS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STEPS / "15-dns-server"))
from dns_server import ZONE, build_response, parse_query

QTYPE_A = 1


def recv_exactly(conn, size):
    buf = b""
    while len(buf) < size:
        chunk = conn.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("peer closed")
        buf += chunk
    return buf


def handle(conn):
    with conn:
        while True:
            try:
                size = int.from_bytes(recv_exactly(conn, 2), "big")
                packet = recv_exactly(conn, size)
            except ConnectionError:
                return

            try:
                _, name, qtype, _, question_end = parse_query(packet)
            except (ValueError, IndexError):
                return

            if qtype != QTYPE_A:
                response = build_response(packet, question_end, None, 0)  # NODATA
            else:
                ip = ZONE.get(name.lower())
                response = build_response(packet, question_end, ip, 0 if ip else 3)
            conn.sendall(len(response).to_bytes(2, "big") + response)


def serve(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"listening on {host}:{server.getsockname()[1]}", flush=True)

        while True:
            conn, _ = server.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5353)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        pass
