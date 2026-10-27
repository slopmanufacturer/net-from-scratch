import pathlib
import socket
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from testkit import start_server, stop

server = pathlib.Path(__file__).with_name("echo_server.py")
proc, port = start_server(server)
try:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(b"hello\n")
        assert sock.recv(1024) == b"hello\n"

        sock.sendall(b"second line\n")
        assert sock.recv(1024) == b"second line\n"
finally:
    stop(proc)

print("ok")
