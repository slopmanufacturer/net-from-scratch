#!/usr/bin/env python3
"""Step 20: DNS, TCP, TLS, and HTTP in one command."""

import argparse
import pathlib
import socket
import ssl
import sys
from urllib.parse import urljoin, urlsplit

CERTS = pathlib.Path(__file__).resolve().parents[2] / ".certs"


def connect(host, port):
    last_error = None
    for family, socktype, proto, _, sockaddr in socket.getaddrinfo(
        host, port, type=socket.SOCK_STREAM
    ):
        sock = socket.socket(family, socktype, proto)
        sock.settimeout(10)
        try:
            sock.connect(sockaddr)
            return sock
        except OSError as exc:
            last_error = exc
            sock.close()
    raise last_error


def read_chunked(reader):
    body = b""
    while True:
        size = int(reader.readline().split(b";")[0].strip(), 16)
        if size == 0:
            reader.readline()
            return body
        body += reader.read(size)
        reader.read(2)


def read_response(sock):
    reader = sock.makefile("rb")
    status_line = reader.readline().decode("latin-1").strip()

    headers = {}
    while True:
        line = reader.readline()
        if line in (b"\r\n", b"\n", b""):
            break
        name, _, value = line.decode("latin-1").partition(":")
        headers[name.strip().lower()] = value.strip()

    if headers.get("transfer-encoding", "").lower() == "chunked":
        body = read_chunked(reader)
    elif "content-length" in headers:
        body = reader.read(int(headers["content-length"]))
    else:
        body = reader.read()

    return status_line, headers, body


def fetch(url, args, hops=0):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise SystemExit(f"unsupported scheme: {parts.scheme}")

    host = parts.hostname
    port = parts.port or (443 if parts.scheme == "https" else 80)
    path = parts.path or "/"
    if parts.query:
        path += "?" + parts.query

    sock = connect(host, port)
    if parts.scheme == "https":
        if args.insecure:
            context = ssl._create_unverified_context()
        else:
            context = ssl.create_default_context(cafile=args.cafile)
        sock = context.wrap_socket(sock, server_hostname=host)

    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {parts.netloc}\r\n"
        f"User-Agent: mini-curl/1.0\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    sock.sendall(request.encode("latin-1"))
    status_line, headers, body = read_response(sock)
    sock.close()

    if args.follow and headers.get("location") and hops < 5:
        return fetch(urljoin(url, headers["location"]), args, hops + 1)

    return status_line, headers, body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("-i", "--include", action="store_true", help="print headers too")
    parser.add_argument("-L", "--follow", action="store_true", help="follow redirects")
    parser.add_argument("-k", "--insecure", action="store_true", help="skip certificate checks")
    parser.add_argument("--cafile", default=str(CERTS / "ca.pem"))
    args = parser.parse_args()

    if args.url.startswith("https") and not args.insecure and not pathlib.Path(args.cafile).exists():
        sys.exit("run `python tools/make_cert.py` first, or pass -k")

    try:
        status_line, headers, body = fetch(args.url, args)
    except (OSError, ssl.SSLError) as exc:
        sys.exit(f"mini-curl: {exc}")

    if args.include:
        lines = [status_line] + [f"{name}: {value}" for name, value in headers.items()]
        sys.stdout.buffer.write(("\n".join(lines) + "\n\n").encode("latin-1"))

    sys.stdout.buffer.write(body)
    sys.stdout.flush()

    code = int(status_line.split(" ")[1]) if " " in status_line else 0
    return 0 if code < 400 else 1


if __name__ == "__main__":
    sys.exit(main())
