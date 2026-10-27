#!/usr/bin/env python3
"""Step 04: a line protocol. SET, GET, DEL over one connection."""

import argparse
import socket
import threading

store = {}
lock = threading.Lock()


def read_line(sock, buf):
    while b"\n" not in buf:
        chunk = sock.recv(1024)
        if not chunk:
            return None, buf
        buf += chunk
    line, _, buf = buf.partition(b"\n")
    return line.rstrip(b"\r"), buf


def reply(conn, text):
    conn.sendall(text.encode() + b"\n")


def handle(conn):
    buf = b""
    with conn:
        while True:
            line, buf = read_line(conn, buf)
            if line is None:
                return

            parts = line.decode(errors="replace").split(" ", 2)
            command = parts[0].upper()

            if command == "SET" and len(parts) == 3:
                with lock:
                    store[parts[1]] = parts[2]
                reply(conn, "OK")
            elif command == "GET" and len(parts) == 2:
                with lock:
                    value = store.get(parts[1])
                reply(conn, "NONE" if value is None else f"VALUE {value}")
            elif command == "DEL" and len(parts) == 2:
                with lock:
                    store.pop(parts[1], None)
                reply(conn, "OK")
            elif command == "QUIT":
                reply(conn, "BYE")
                return
            else:
                reply(conn, "ERR unknown command")


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
