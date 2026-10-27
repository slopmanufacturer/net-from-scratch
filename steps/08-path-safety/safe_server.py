#!/usr/bin/env python3
"""Step 08: keep requests inside the document root."""

import argparse
import socket
import threading
from pathlib import Path
from urllib.parse import unquote

TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".png": "image/png",
}


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


def resolve(root, url_path):
    """Return a file path inside root, or None if the request escapes."""
    root = root.resolve()
    path = unquote(url_path.split("?", 1)[0])
    target = (root / path.lstrip("/")).resolve()
    if target != root and root not in target.parents:
        return None
    return target


def serve_file(root, url_path):
    target = resolve(root, url_path)
    if target is None:
        return "403 Forbidden", b"outside the root\n", "text/plain; charset=utf-8"

    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        return "404 Not Found", b"not found\n", "text/plain; charset=utf-8"

    body = target.read_bytes()
    content_type = TYPES.get(target.suffix, "application/octet-stream")
    return "200 OK", body, content_type


def handle(conn, root):
    with conn:
        request = read_request(conn)
        if request is None:
            return
        _, path, _, _, _ = request
        status, body, content_type = serve_file(root, path)
        conn.sendall(build_response(status, body, content_type))


def serve(host, port, root):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"listening on {host}:{server.getsockname()[1]}", flush=True)

        while True:
            conn, _ = server.accept()
            threading.Thread(target=handle, args=(conn, root), daemon=True).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--root", default=Path(__file__).with_name("site"))
    args = parser.parse_args()
    try:
        serve(args.host, args.port, Path(args.root))
    except KeyboardInterrupt:
        pass
