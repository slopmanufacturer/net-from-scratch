#!/usr/bin/env python3
"""Step 14: build a DNS query byte by byte, then parse the answer."""

import argparse
import random
import socket
import struct
import sys

QTYPE_A = 1
QCLASS_IN = 1


def encode_name(name):
    out = b""
    for label in name.rstrip(".").split("."):
        raw = label.encode("idna")
        if not 0 < len(raw) < 64:
            raise ValueError(f"bad label: {label!r}")
        out += bytes([len(raw)]) + raw
    return out + b"\x00"


def build_query(name, qid, qtype=QTYPE_A):
    header = struct.pack("!HHHHHH", qid, 0x0100, 1, 0, 0, 0)  # RD = 1
    return header + encode_name(name) + struct.pack("!HH", qtype, QCLASS_IN)


def read_name(message, offset, depth=0):
    if depth > 10:
        raise ValueError("compression pointer loop")

    labels = []
    while True:
        length = message[offset]
        if length == 0:
            offset += 1
            break
        if length & 0xC0 == 0xC0:
            pointer = struct.unpack("!H", message[offset:offset + 2])[0] & 0x3FFF
            label, _ = read_name(message, pointer, depth + 1)
            labels.append(label)
            offset += 2
            break
        labels.append(message[offset + 1:offset + 1 + length].decode("idna"))
        offset += 1 + length
    return ".".join(labels), offset


def parse_response(message):
    qid, flags, qdcount, ancount, _, _ = struct.unpack("!HHHHHH", message[:12])
    rcode = flags & 0x000F

    offset = 12
    for _ in range(qdcount):
        _, offset = read_name(message, offset)
        offset += 4  # qtype, qclass

    answers = []
    for _ in range(ancount):
        name, offset = read_name(message, offset)
        rtype, _, ttl, rdlength = struct.unpack("!HHIH", message[offset:offset + 10])
        offset += 10
        rdata = message[offset:offset + rdlength]
        offset += rdlength
        value = socket.inet_ntoa(rdata) if rtype == QTYPE_A and rdlength == 4 else rdata.hex()
        answers.append((name, rtype, ttl, value))

    return qid, rcode, answers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--server", default="1.1.1.1")
    parser.add_argument("--port", type=int, default=53)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--show-packet", action="store_true")
    args = parser.parse_args()

    qid = random.randrange(0, 65536)
    query = build_query(args.name, qid)
    if args.show_packet:
        print(query.hex())

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(args.timeout)
        try:
            sock.sendto(query, (args.server, args.port))
            response, _ = sock.recvfrom(4096)
        except socket.timeout:
            print(f"no response from {args.server} after {args.timeout}s")
            return 1

    try:
        got_id, rcode, answers = parse_response(response)
    except (ValueError, IndexError, struct.error) as exc:
        print(f"could not parse the response: {exc}")
        return 1

    if got_id != qid:
        print(f"response id {got_id} does not match query id {qid}")
        return 1

    if rcode != 0:
        print(f"{args.name}  rcode {rcode}")
        return 1

    for name, _, ttl, value in answers:
        print(f"{name}  {ttl}s  A  {value}")

    if not answers:
        print(f"{args.name}  no answers")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
