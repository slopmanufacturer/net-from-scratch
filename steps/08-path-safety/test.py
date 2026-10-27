import pathlib
import socket
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from testkit import start_server, stop


def fetch(port, raw_path):
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        request = f"GET {raw_path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode()
        sock.sendall(request)
        data = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
    head, _, body = data.partition(b"\r\n\r\n")
    return head.decode("latin-1"), body


proc, port = start_server(HERE / "safe_server.py")
try:
    head, body = fetch(port, "/sub/page.html")
    assert head.startswith("HTTP/1.1 200 OK"), head
    assert b"nested" in body

    head, _ = fetch(port, "/../secret.txt")
    assert head.startswith("HTTP/1.1 403 Forbidden"), head

    head, _ = fetch(port, "/%2e%2e/secret.txt")
    assert head.startswith("HTTP/1.1 403 Forbidden"), head

    head, _ = fetch(port, "/sub/../../secret.txt")
    assert head.startswith("HTTP/1.1 403 Forbidden"), head

    head, _ = fetch(port, "/missing.html")
    assert head.startswith("HTTP/1.1 404 Not Found"), head
finally:
    stop(proc)

print("ok")
