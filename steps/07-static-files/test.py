import pathlib
import socket
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from testkit import start_server, stop


def fetch(port, path):
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(f"GET {path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode())
        data = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
    head, _, body = data.partition(b"\r\n\r\n")
    return head.decode("latin-1"), body


proc, port = start_server(HERE / "static_server.py")
try:
    head, body = fetch(port, "/")
    assert head.startswith("HTTP/1.1 200 OK"), head
    assert "Content-Type: text/html; charset=utf-8" in head
    assert b"<title>static</title>" in body

    head, body = fetch(port, "/style.css")
    assert head.startswith("HTTP/1.1 200 OK"), head
    assert "Content-Type: text/css; charset=utf-8" in head
    assert b"font-family" in body

    head, body = fetch(port, "/missing.txt")
    assert head.startswith("HTTP/1.1 404 Not Found"), head
    assert body == b"not found\n"
finally:
    stop(proc)

print("ok")
