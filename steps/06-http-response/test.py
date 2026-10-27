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
    lines = head.decode("latin-1").split("\r\n")
    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    return lines[0], headers, body


proc, port = start_server(HERE / "http_server.py")
try:
    status, headers, body = fetch(port, "/")
    assert status == "HTTP/1.1 200 OK", status
    assert headers["content-type"] == "text/html; charset=utf-8"
    assert int(headers["content-length"]) == len(body)
    assert b"<h1>It works</h1>" in body

    status, headers, body = fetch(port, "/health")
    assert status == "HTTP/1.1 200 OK", status
    assert body == b"ok\n"

    status, headers, body = fetch(port, "/nope")
    assert status == "HTTP/1.1 404 Not Found", status
    assert int(headers["content-length"]) == len(body)
finally:
    stop(proc)

print("ok")
