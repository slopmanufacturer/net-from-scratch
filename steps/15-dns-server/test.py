import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from testkit import start_server, stop

CLIENT = HERE.parent / "14-dns-query" / "dns_query.py"


def query(port, name):
    return subprocess.run(
        [sys.executable, str(CLIENT), name, "--server", "127.0.0.1", "--port", str(port)],
        capture_output=True, text=True, timeout=10,
    )


proc, port = start_server(HERE / "dns_server.py")
try:
    result = query(port, "api.example.com")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "93.184.216.35" in result.stdout, result.stdout

    result = query(port, "example.com")
    assert "93.184.216.34" in result.stdout

    result = query(port, "nope.example.com")
    assert result.returncode == 1
    assert "rcode 3" in result.stdout, result.stdout
finally:
    stop(proc)

print("ok")
