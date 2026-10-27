#!/usr/bin/env python3
"""Step 09: more than one request per connection."""

import argparse
import socket
import threading


def read_request(conn, buf):
    """Return ((method, path, version, headers), leftover) or (None, buf)."""
    while b"\r\n\r\n" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            return None, buf
        buf += chunk

    head, _, buf = buf.partition(b"\r\n\r\n")
    lines = head.decode("iso-8859-1").split("\r\n")
    method, path, version = lines[0].split(" ", 2)
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    return (method, path, version, headers), buf


def build_response(body, keep_alive):
    head = [
        "HTTP/1.1 200 OK",
        "Content-Type: text/plain; charset=utf-8",
        f"Content-Length: {len(body)}",
        f"Connection: {'keep-alive' if keep_alive else 'close'}",
    ]
    return ("\r\n".join(head) + "\r\n\r\n").encode("latin-1") + body


def wants_close(version, headers):
    connection = headers.get("connection", "").lower()
    if connection == "close":
        return True
    if version == "HTTP/1.0" and connection != "keep-alive":
        return True
    return False


def handle(conn):
    buf = b""
    count = 0
    with conn:
        while True:
            request, buf = read_request(conn, buf)
            if request is None:
                return

            method, path, version, headers = request
            count += 1
            keep_alive = not wants_close(version, headers)
            body = f"request {count} on this connection: {method} {path}\n".encode()
            conn.sendall(build_response(body, keep_alive))
            if not keep_alive:
                return


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
