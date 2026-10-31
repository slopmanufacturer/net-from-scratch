import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from testkit import start_server, stop

CERTS = ROOT / ".certs"
if not (CERTS / "server.pem").exists():
    print("skipped: no certificates (run tools/make_cert.py)")
    raise SystemExit(77)

proc, port = start_server(HERE / "https_server.py")
try:
    result = subprocess.run(
        [sys.executable, str(HERE / "https_client.py"), "/", str(port)],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "HTTP/1.1 200 OK" in result.stdout, result.stdout
    assert "<title>net-from-scratch</title>" in result.stdout, result.stdout

    result = subprocess.run(
        [sys.executable, str(HERE / "https_client.py"), "/api/time", str(port)],
        capture_output=True, text=True, timeout=15,
    )
    assert '"time"' in result.stdout, result.stdout

    result = subprocess.run(
        [sys.executable, str(HERE / "https_client.py"), "/", str(port), "--insecure"],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert "HTTP/1.1 200 OK" in result.stdout
finally:
    stop(proc)

print("ok")
