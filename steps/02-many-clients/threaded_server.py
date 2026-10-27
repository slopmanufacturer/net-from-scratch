#!/usr/bin/env python3
"""Step 02: one thread per connection, so a quiet client cannot block the rest."""

import argparse
import socket
import threading

count = 0
lock = threading.Lock()


def handle(conn, addr, number):
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
    print(f"client {number} from {addr[0]}:{addr[1]} disconnected", flush=True)


def serve(host, port):
    global count

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"listening on {host}:{server.getsockname()[1]}", flush=True)

        while True:
            conn, addr = server.accept()
            with lock:
                count += 1
                number = count
            print(f"client {number} from {addr[0]}:{addr[1]}", flush=True)
            threading.Thread(target=handle, args=(conn, addr, number), daemon=True).start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        pass
