import pathlib
import socket
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
sys.path.insert(0, str(HERE))
from testkit import start_server, stop
from framed_server import recv_exactly, recv_message, send_message

proc, port = start_server(HERE / "framed_server.py")
try:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        assert [recv_message(sock) for _ in range(3)] == [b"alpha", b"beta", b"gamma"]

        blob = b""
        for message in (b"one", b"two"):
            blob += len(message).to_bytes(4, "big") + message
        sock.sendall(blob)
        assert recv_message(sock) == b"ONE"
        assert recv_message(sock) == b"TWO"

    # A message split across two writes still parses as one message.
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        for _ in range(3):
            recv_message(sock)
        send_message(sock, b"split")
        assert recv_message(sock) == b"SPLIT"
finally:
    stop(proc)

print("ok")
