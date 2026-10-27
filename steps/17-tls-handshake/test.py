import pathlib
import socket
import ssl
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

proc, port = start_server(HERE / "tls_server.py")
try:
    result = subprocess.run(
        [sys.executable, str(HERE / "tls_client.py"), str(port)],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "TLSv1.3" in result.stdout or "TLSv1.2" in result.stdout, result.stdout
    assert "HELLO OVER TLS" in result.stdout, result.stdout

    # Without the CA, verification must fail.
    context = ssl.create_default_context()
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        try:
            context.wrap_socket(sock, server_hostname="localhost")
        except ssl.SSLCertVerificationError:
            pass
        else:
            raise AssertionError("a self-signed certificate was trusted by default")
finally:
    stop(proc)

print("ok")
