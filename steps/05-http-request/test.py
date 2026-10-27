import pathlib
import socket
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from testkit import start_server, stop


def read_all(sock):
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            return data
        data += chunk


proc, port = start_server(HERE / "request_server.py")
try:
    # The request is sent one byte at a time: the parser has to buffer.
    request = (
        b"GET /hello?x=1 HTTP/1.1\r\n"
        b"Host: localhost\r\n"
        b"X-Test: yes\r\n"
        b"\r\n"
    )
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        for byte in request:
            sock.sendall(bytes([byte]))
        response = read_all(sock).decode()

    head, body = response.split("\r\n\r\n", 1)
    assert head.startswith("HTTP/1.1 200 OK"), head
    assert "method: GET" in body
    assert "path: /hello?x=1" in body
    assert "version: HTTP/1.1" in body
    assert "host: localhost" in body
    assert "x-test: yes" in body

    # An empty connection should not crash the server.
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        pass

    # The server still answers afterwards.
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(b"POST /x HTTP/1.0\r\n\r\n")
        response = read_all(sock).decode()
    assert "method: POST" in response
    assert "version: HTTP/1.0" in response
finally:
    stop(proc)

print("ok")
