import pathlib
import socket
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from testkit import start_server, stop


def read_response(reader):
    status = reader.readline().decode().strip()
    headers = {}
    while True:
        line = reader.readline().decode()
        if line in ("\r\n", "\n", ""):
            break
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()
    length = int(headers.get("content-length", 0))
    body = reader.read(length)
    return status, headers, body


proc, port = start_server(HERE / "keepalive_server.py")
try:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        reader = sock.makefile("rb")

        sock.sendall(b"GET /a HTTP/1.1\r\nHost: localhost\r\n\r\n")
        status, headers, body = read_response(reader)
        assert status == "HTTP/1.1 200 OK", status
        assert headers["connection"] == "keep-alive"
        assert body == b"request 1 on this connection: GET /a\n"

        sock.sendall(b"GET /b HTTP/1.1\r\nHost: localhost\r\n\r\n")
        status, headers, body = read_response(reader)
        assert body == b"request 2 on this connection: GET /b\n"

        # Two pipelined requests in one write.
        sock.sendall(
            b"GET /c HTTP/1.1\r\nHost: localhost\r\n\r\n"
            b"GET /d HTTP/1.1\r\nHost: localhost\r\n\r\n"
        )
        _, _, body = read_response(reader)
        assert body == b"request 3 on this connection: GET /c\n"
        _, _, body = read_response(reader)
        assert body == b"request 4 on this connection: GET /d\n"

        sock.sendall(b"GET /bye HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        status, headers, body = read_response(reader)
        assert headers["connection"] == "close"
        assert body == b"request 5 on this connection: GET /bye\n"
        assert reader.read() == b""
finally:
    stop(proc)

print("ok")
