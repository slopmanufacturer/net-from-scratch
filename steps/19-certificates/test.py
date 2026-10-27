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
    raise SystemExit(0)

proc, port = start_server(ROOT / "steps" / "18-https-server" / "https_server.py")
try:
    result = subprocess.run(
        [sys.executable, str(HERE / "inspect_cert.py"), "--port", str(port)],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "commonName: localhost" in result.stdout, result.stdout
    assert "net-from-scratch CA" in result.stdout, result.stdout
    assert "DNS: localhost" in result.stdout, result.stdout
    assert "IP Address: 127.0.0.1" in result.stdout, result.stdout
    assert "valid to:" in result.stdout
finally:
    stop(proc)

print("ok")
