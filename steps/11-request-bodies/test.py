import json
import pathlib
import socket
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from testkit import start_server, stop


def read_response(sock):
    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    head, _, body = data.partition(b"\r\n\r\n")
    status = head.split(b"\r\n")[0].decode()
    return status, json.loads(body)


proc, port = start_server(HERE / "json_server.py")
try:
    payload = b'{"name": "ada"}'
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(
            b"POST /echo HTTP/1.1\r\nHost: localhost\r\n"
            b"Content-Type: application/json\r\n"
            + f"Content-Length: {len(payload)}\r\n\r\n".encode()
            + payload
        )
        status, body = read_response(sock)
    assert status == "HTTP/1.1 200 OK", status
    assert body == {"hello": "ada", "bytes": len(payload)}, body

    # Header first, then the body in two pieces with a pause.
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        payload = b'{"name": "grace"}'
        sock.sendall(
            b"POST /echo HTTP/1.1\r\nHost: localhost\r\n"
            + f"Content-Length: {len(payload)}\r\n\r\n".encode()
        )
        time.sleep(0.1)
        sock.sendall(payload[:5])
        time.sleep(0.1)
        sock.sendall(payload[5:])
        status, body = read_response(sock)
    assert status == "HTTP/1.1 200 OK", status
    assert body["hello"] == "grace"

    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(b"POST /echo HTTP/1.1\r\nHost: localhost\r\n\r\n")
        status, body = read_response(sock)
    assert status == "HTTP/1.1 411 Length Required", status

    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        bad = b"not json"
        sock.sendall(
            b"POST /echo HTTP/1.1\r\nHost: localhost\r\n"
            + f"Content-Length: {len(bad)}\r\n\r\n".encode()
            + bad
        )
        status, body = read_response(sock)
    assert status == "HTTP/1.1 400 Bad Request", status
    assert "bad json" in body["error"]
finally:
    stop(proc)

print("ok")
