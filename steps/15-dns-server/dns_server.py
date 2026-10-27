#!/usr/bin/env python3
"""Step 15: a stub resolver. It answers from a dictionary and nothing else."""

import argparse
import pathlib
import socket
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "14-dns-query"))
from dns_query import read_name

ZONE = {
    "example.com": "93.184.216.34",
    "api.example.com": "93.184.216.35",
    "www.example.com": "93.184.216.34",
    "localhost.test": "127.0.0.1",
}

QTYPE_A = 1


def parse_query(packet):
    qid, _, qdcount = struct.unpack("!HHH", packet[:6])
    if qdcount != 1:
        raise ValueError("this server only answers one question at a time")

    name, offset = read_name(packet, 12)
    qtype, qclass = struct.unpack("!HH", packet[offset:offset + 4])
    return qid, name, qtype, qclass, offset + 4


def build_response(packet, question_end, ip, rcode=0):
    question = packet[12:question_end]
    if ip is None:
        header = packet[:2] + struct.pack("!HHHHH", 0x8180 | rcode, 1, 0, 0, 0)
        return header + question

    header = packet[:2] + struct.pack("!HHHHH", 0x8180, 1, 1, 0, 0)
    answer = b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 60, 4) + socket.inet_aton(ip)
    return header + question + answer


def serve(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        print(f"listening on {host}:{sock.getsockname()[1]}", flush=True)

        while True:
            packet, addr = sock.recvfrom(4096)
            try:
                _, name, qtype, _, question_end = parse_query(packet)
            except (ValueError, IndexError, struct.error):
                continue

            if qtype != QTYPE_A:
                response = build_response(packet, question_end, None, 0)  # NODATA
            else:
                ip = ZONE.get(name.lower())
                response = build_response(packet, question_end, ip, 0 if ip else 3)
            sock.sendto(response, addr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5353)
    args = parser.parse_args()
    try:
        serve(args.host, args.port)
    except KeyboardInterrupt:
        pass
