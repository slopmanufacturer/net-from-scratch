#!/usr/bin/env python3
"""Step 17: put TLS in front of a socket and watch what the handshake negotiates."""

import argparse
import pathlib
import socket
import ssl
import sys

CERTS = pathlib.Path(__file__).resolve().parents[2] / ".certs"


def serve(host, port):
    if not (CERTS / "server.pem").exists():
        sys.exit("run `python tools/make_cert.py` first")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERTS / "server.pem", CERTS / "server.key")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"listening on {host}:{server.getsockname()[1]}", flush=True)

        while True:
            conn, _ = server.accept()
            try:
                with context.wrap_socket(conn, server_side=True) as tls:
                    print(f"handshake: {tls.version()} {tls.cipher()[0]}", flush=True)
                    data = tls.recv(1024)
                    tls.sendall(data.upper())
            except ssl.SSLError as exc:
                conn.close()
                print(f"handshake failed: {exc}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8443)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        pass
