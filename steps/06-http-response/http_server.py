#!/usr/bin/env python3
"""Step 06: a real response, with a status line, headers, and a body."""

import argparse
import socket
import threading

PAGE = b"""<!doctype html>
<html><head><title>hello</title></head>
<body><h1>It works</h1><p>Served by a socket.</p></body></html>
"""


def read_request(conn):
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


def build_response(status, body, content_type="text/plain; charset=utf-8"):
    head = [
        f"HTTP/1.1 {status}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
    ]
    return ("\r\n".join(head) + "\r\n\r\n").encode("latin-1") + body


def route(path):
    if path == "/":
        return "200 OK", PAGE, "text/html; charset=utf-8"
    if path == "/health":
        return "200 OK", b"ok\n", "text/plain; charset=utf-8"
    return "404 Not Found", b"no such page\n", "text/plain; charset=utf-8"


def handle(conn):
    with conn:
        request = read_request(conn)
        if request is None:
            return
        _, path, _, _, _ = request
        status, body, content_type = route(path)
        conn.sendall(build_response(status, body, content_type))


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
