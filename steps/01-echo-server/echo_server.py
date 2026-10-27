#!/usr/bin/env python3
"""Step 01: one TCP connection, echoed back byte for byte."""

import argparse
import socket


def handle(conn):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)


def serve(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"listening on {host}:{server.getsockname()[1]}", flush=True)

        conn, addr = server.accept()
        print(f"connection from {addr[0]}:{addr[1]}", flush=True)
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
