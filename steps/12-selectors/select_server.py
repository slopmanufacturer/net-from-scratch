#!/usr/bin/env python3
"""Step 12: one thread, many connections, no threads at all."""

import argparse
import selectors
import socket

selector = selectors.DefaultSelector()


class Client:
    __slots__ = ("sock", "inbuf", "outbuf", "closed")

    def __init__(self, sock):
        self.sock = sock
        self.inbuf = b""
        self.outbuf = b""
        self.closed = False


def response(path):
    body = f"path={path}\n".encode()
    head = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    )
    return head.encode("latin-1") + body


def drop(client):
    if client.closed:
        return
    client.closed = True
    try:
        selector.unregister(client.sock)
    except KeyError:
        pass
    client.sock.close()


def on_accept(server):
    try:
        conn, _ = server.accept()
    except BlockingIOError:
        return
    conn.setblocking(False)
    selector.register(conn, selectors.EVENT_READ, Client(conn))


def on_read(client):
    try:
        data = client.sock.recv(4096)
    except BlockingIOError:
        return
    except ConnectionResetError:
        drop(client)
        return

    if not data:
        drop(client)
        return

    client.inbuf += data
    if b"\r\n\r\n" not in client.inbuf:
        return

    head = client.inbuf.split(b"\r\n\r\n", 1)[0].decode("latin-1")
    parts = head.split(" ")
    path = parts[1] if len(parts) > 1 else "/"

    client.outbuf += response(path)
    selector.modify(client.sock, selectors.EVENT_READ | selectors.EVENT_WRITE, client)


def on_write(client):
    try:
        sent = client.sock.send(client.outbuf)
    except BlockingIOError:
        return
    except ConnectionResetError:
        drop(client)
        return

    client.outbuf = client.outbuf[sent:]
    if not client.outbuf:
        drop(client)


def serve(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(False)
        server.bind((host, port))
        server.listen()
        print(f"listening on {host}:{server.getsockname()[1]}", flush=True)
        selector.register(server, selectors.EVENT_READ)

        while True:
            for key, mask in selector.select():
                if key.fileobj is server:
                    on_accept(server)
                    continue

                client = key.data
                if client.closed:
                    continue
                if mask & selectors.EVENT_READ:
                    on_read(client)
                if mask & selectors.EVENT_WRITE and not client.closed:
                    on_write(client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        pass
