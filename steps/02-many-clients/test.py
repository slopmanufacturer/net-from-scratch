import pathlib
import socket
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "tools"))
from testkit import start_server, stop

server = pathlib.Path(__file__).with_name("threaded_server.py")
proc, port = start_server(server)
try:
    quiet = socket.create_connection(("127.0.0.1", port), timeout=5)
    loud = socket.create_connection(("127.0.0.1", port), timeout=5)

    loud.sendall(b"still works\n")
    assert loud.recv(1024) == b"still works\n"

    quiet.sendall(b"i was here all along\n")
    assert quiet.recv(1024) == b"i was here all along\n"

    extra = [socket.create_connection(("127.0.0.1", port), timeout=5) for _ in range(5)]
    for i, sock in enumerate(extra):
        sock.sendall(f"client {i}\n".encode())
    for i, sock in enumerate(extra):
        assert sock.recv(1024) == f"client {i}\n".encode()

    quiet.close()
    loud.close()
    for sock in extra:
        sock.close()
finally:
    stop(proc)

print("ok")
