import pathlib
import socket
import sys
import time

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


proc, port = start_server(HERE / "select_server.py")
try:
    sockets = [socket.create_connection(("127.0.0.1", port), timeout=5) for _ in range(3)]

    # A request split across two writes must still parse.
    sockets[0].sendall(b"GET /slow HTTP/1.1\r\nHost: localhost\r\n")
    time.sleep(0.1)
    sockets[0].sendall(b"\r\n")

    sockets[1].sendall(b"GET /b HTTP/1.1\r\nHost: localhost\r\n\r\n")
    sockets[2].sendall(b"GET /c HTTP/1.1\r\nHost: localhost\r\n\r\n")

    bodies = [read_all(sock).split(b"\r\n\r\n", 1)[1] for sock in sockets]
    assert bodies == [b"path=/slow\n", b"path=/b\n", b"path=/c\n"], bodies

    for sock in sockets:
        sock.close()
finally:
    stop(proc)

print("ok")
