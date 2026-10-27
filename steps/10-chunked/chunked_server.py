#!/usr/bin/env python3
"""Step 10: send the body in chunks, without knowing its length up front."""

import argparse
import socket
import threading
import time

PARTS = [b"one ", b"two ", b"three\n"]


def read_request(conn):
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        buf += chunk
    return buf.partition(b"\r\n\r\n")[0].decode("iso-8859-1")


def handle(conn):
    with conn:
        if read_request(conn) is None:
            return

        conn.sendall(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"Transfer-Encoding: chunked\r\n"
            b"Connection: close\r\n"
            b"\r\n"
        )

        for part in PARTS:
            conn.sendall(f"{len(part):x}\r\n".encode() + part + b"\r\n")
            time.sleep(0.2)

        conn.sendall(b"0\r\n\r\n")


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
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        pass
