import pathlib
import socket
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from testkit import start_server, stop

proc, port = start_server(HERE / "kv_server.py")
try:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        reader = sock.makefile("r")

        sock.sendall(b"SET name ada\n")
        assert reader.readline() == "OK\n"

        sock.sendall(b"GET name\n")
        assert reader.readline() == "VALUE ada\n"

        sock.sendall(b"GET missing\n")
        assert reader.readline() == "NONE\n"

        # Two commands in one write: the buffer has to split them.
        sock.sendall(b"SET city berlin\nGET city\n")
        assert reader.readline() == "OK\n"
        assert reader.readline() == "VALUE berlin\n"

        sock.sendall(b"DEL city\nGET city\n")
        assert reader.readline() == "OK\n"
        assert reader.readline() == "NONE\n"

        sock.sendall(b"WAT\n")
        assert reader.readline() == "ERR unknown command\n"

        sock.sendall(b"SET note a value with spaces\nGET note\n")
        assert reader.readline() == "OK\n"
        assert reader.readline() == "VALUE a value with spaces\n"

        sock.sendall(b"QUIT\n")
        assert reader.readline() == "BYE\n"
finally:
    stop(proc)

print("ok")
