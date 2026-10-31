import http.server
import pathlib
import subprocess
import sys
import threading

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from testkit import start_server, stop

CERTS = ROOT / ".certs"


def run(url, *extra):
    return subprocess.run(
        [sys.executable, str(HERE / "mini_curl.py"), url, *extra],
        capture_output=True, text=True, timeout=20,
    )


# Plain HTTP, chunked body.
chunked, port = start_server(ROOT / "steps" / "10-chunked" / "chunked_server.py")
try:
    result = run(f"http://127.0.0.1:{port}/")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "one two three\n", result.stdout
finally:
    stop(chunked)

# HTTPS with verification against the local CA.
if (CERTS / "server.pem").exists():
    https, port = start_server(ROOT / "steps" / "18-https-server" / "https_server.py")
    try:
        result = run(f"https://localhost:{port}/")
        assert result.returncode == 0, result.stderr
        assert "<title>net-from-scratch</title>" in result.stdout, result.stdout

        result = run(f"https://localhost:{port}/", "-i")
        assert result.stdout.startswith("HTTP/1.1 200 OK"), result.stdout
        assert "content-type: text/html" in result.stdout
    finally:
        stop(https)

    # Redirect: a stock http.server sends 302, mini-curl follows it.
    target, target_port = start_server(ROOT / "steps" / "13-real-page" / "app_server.py")
    try:
        class Redirect(http.server.BaseHTTPRequestHandler):
            destination = ""

            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", self.destination)
                self.end_headers()

            def log_message(self, *args):
                pass

        Redirect.destination = f"http://127.0.0.1:{target_port}/"
        redirect = http.server.HTTPServer(("127.0.0.1", 0), Redirect)
        threading.Thread(target=redirect.serve_forever, daemon=True).start()

        result = run(f"http://127.0.0.1:{redirect.server_port}/", "-L")
        assert result.returncode == 0, result.stderr
        assert "<title>net-from-scratch</title>" in result.stdout, result.stdout

        redirect.shutdown()
    finally:
        stop(target)
else:
    print("skipped the HTTPS half: no certificates (run tools/make_cert.py)")
    raise SystemExit(77)

print("ok")
