#!/usr/bin/env python3
"""Step 03: TCP gives you bytes, not messages. Length prefixes give you messages."""

import argparse
import socket


def send_message(sock, payload):
    sock.sendall(len(payload).to_bytes(4, "big") + payload)


def recv_exactly(sock, size):
    buf = b""
    while len(buf) < size:
        chunk = sock.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("peer closed")
        buf += chunk
    return buf


def recv_message(sock):
    size = int.from_bytes(recv_exactly(sock, 4), "big")
    return recv_exactly(sock, size)


def handle(conn):
    with conn:
        # Three messages, one sendall. On the wire this is a single run of bytes.
        blob = b""
        for message in (b"alpha", b"beta", b"gamma"):
            blob += len(message).to_bytes(4, "big") + message
        conn.sendall(blob)

        while True:
            try:
                message = recv_message(conn)
            except (ConnectionError, OSError):
                return
            send_message(conn, message.upper())


def serve(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"listening on {host}:{server.getsockname()[1]}", flush=True)

        while True:
            conn, _ = server.accept()
            handle(conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        pass
