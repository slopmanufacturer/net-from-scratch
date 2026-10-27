import pathlib
import socket
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
sys.path.insert(0, str(HERE.parents[0] / "14-dns-query"))
from testkit import start_server, stop
from dns_query import build_query, parse_response


def query(port, name):
    return subprocess.run(
        [sys.executable, str(HERE / "tcp_query.py"), name, "--port", str(port)],
        capture_output=True, text=True, timeout=10,
    )


def recv_exactly(sock, size):
    buf = b""
    while len(buf) < size:
        chunk = sock.recv(size - len(buf))
        if not chunk:
            raise ConnectionError("closed")
        buf += chunk
    return buf


proc, port = start_server(HERE / "tcp_server.py")
try:
    result = query(port, "www.example.com")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "93.184.216.34" in result.stdout, result.stdout

    result = query(port, "missing.example.com")
    assert result.returncode == 1
    assert "rcode 3" in result.stdout

    # Two queries on one connection: the server keeps it open.
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        for name, expected in (("example.com", "93.184.216.34"),
                               ("api.example.com", "93.184.216.35")):
            packet = build_query(name, 0x4242)
            sock.sendall(len(packet).to_bytes(2, "big") + packet)

            size = int.from_bytes(recv_exactly(sock, 2), "big")
            _, rcode, answers = parse_response(recv_exactly(sock, size))
            assert rcode == 0
            assert answers[0][3] == expected, answers
finally:
    stop(proc)

print("ok")
