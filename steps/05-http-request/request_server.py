#!/usr/bin/env python3
"""Step 05: read a request until the blank line, then parse it."""

import argparse
import socket
import threading


def read_request(conn):
    """Return (method, path, version, headers, leftover) or None."""
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        buf += chunk

    head, _, leftover = buf.partition(b"\r\n\r\n")
    lines = head.decode("iso-8859-1").split("\r\n")
    method, path, version = lines[0].split(" ", 2)

    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()

    return method, path, version, headers, leftover


def build_response(status, body, content_type="text/plain; charset=utf-8", extra=None):
    head = [
        f"HTTP/1.1 {status}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
    ]
    for name, value in (extra or {}).items():
        head.append(f"{name}: {value}")
    return ("\r\n".join(head) + "\r\n\r\n").encode("latin-1") + body


def handle(conn):
    with conn:
        request = read_request(conn)
        if request is None:
            return
        method, path, version, headers, _ = request

        lines = [f"method: {method}", f"path: {path}", f"version: {version}"]
        lines += [f"{name}: {value}" for name, value in headers.items()]
        body = ("\n".join(lines) + "\n").encode()

        conn.sendall(build_response("200 OK", body))


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
