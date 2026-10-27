#!/usr/bin/env python3
"""Step 11: read a request body, which is where Content-Length earns its keep."""

import argparse
import json
import socket
import threading


def read_request(conn):
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        buf += chunk

    head, _, buf = buf.partition(b"\r\n\r\n")
    lines = head.decode("iso-8859-1").split("\r\n")
    method, path, version = lines[0].split(" ", 2)
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    return method, path, version, headers, buf


def read_exactly(conn, buf, size):
    while len(buf) < size:
        chunk = conn.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("peer closed mid-body")
        buf += chunk
    return buf[:size]


def build_response(status, payload, content_type="application/json"):
    body = json.dumps(payload).encode() + b"\n"
    head = [
        f"HTTP/1.1 {status}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
    ]
    return ("\r\n".join(head) + "\r\n\r\n").encode("latin-1") + body


def handle(conn):
    with conn:
        request = read_request(conn)
        if request is None:
            return
        method, path, version, headers, leftover = request

        if method != "POST" or path != "/echo":
            conn.sendall(build_response("404 Not Found", {"error": "no such route"}))
            return

        if "content-length" not in headers:
            conn.sendall(build_response("411 Length Required", {"error": "send a Content-Length"}))
            return

        size = int(headers["content-length"])
        try:
            body = read_exactly(conn, leftover, size)
        except ConnectionError:
            return

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            conn.sendall(build_response("400 Bad Request", {"error": f"bad json: {exc.msg}"}))
            return

        conn.sendall(build_response("200 OK", {
            "hello": payload.get("name", "stranger"),
            "bytes": size,
        }))


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
