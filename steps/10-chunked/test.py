import pathlib
import socket
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from testkit import start_server, stop

proc, port = start_server(HERE / "chunked_server.py")
try:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        reader = sock.makefile("rb")

        status = reader.readline().decode().strip()
        assert status == "HTTP/1.1 200 OK", status

        headers = {}
        while True:
            line = reader.readline().decode()
            if line in ("\r\n", "\n", ""):
                break
            name, _, value = line.partition(":")
            headers[name.strip().lower()] = value.strip()

        assert headers["transfer-encoding"] == "chunked"
        assert "content-length" not in headers

        body = b""
        chunks = 0
        while True:
            size = int(reader.readline().split(b";")[0].strip(), 16)
            if size == 0:
                reader.readline()
                break
            body += reader.read(size)
            assert reader.read(2) == b"\r\n"
            chunks += 1

        assert body == b"one two three\n", body
        assert chunks == 3
finally:
    stop(proc)

print("ok")
