import pathlib
import socket
import struct
import subprocess
import sys
import threading

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dns_query import build_query, encode_name, parse_response, read_name

# --- the wire format -------------------------------------------------------

assert encode_name("example.com") == b"\x07example\x03com\x00"
assert encode_name("www.example.com.") == b"\x03www\x07example\x03com\x00"

query = build_query("example.com", 0x1234)
assert query[:2] == b"\x12\x34"
assert query[2:4] == b"\x01\x00"
assert query[4:6] == b"\x00\x01"


def make_response(packet, ip="93.184.216.34", rcode=0):
    header = packet[:2] + struct.pack("!HHHHH", 0x8180 | rcode, 1, 1 if rcode == 0 else 0, 0, 0)
    question = packet[12:]
    if rcode:
        return header + question
    answer = b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 300, 4) + socket.inet_aton(ip)
    return header + question + answer


# --- parsing, including a compression pointer ------------------------------

qid, rcode, answers = parse_response(make_response(query))
assert qid == 0x1234
assert rcode == 0
assert answers == [("example.com", 1, 300, "93.184.216.34")], answers

name, offset = read_name(b"\x03www\x07example\x03com\x00", 0)
assert name == "www.example.com"
assert offset == 17


# --- the command-line tool against a fake resolver -------------------------

def run_query(response_builder, *extra):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]

    def serve():
        packet, addr = sock.recvfrom(4096)
        sock.sendto(response_builder(packet), addr)

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    try:
        proc = subprocess.run(
            [sys.executable, str(HERE / "dns_query.py"), "example.com",
             "--server", "127.0.0.1", "--port", str(port), *extra],
            capture_output=True, text=True, timeout=10,
        )
    finally:
        sock.close()
    return proc


proc = run_query(make_response)
assert proc.returncode == 0, proc.stderr
assert proc.stdout.strip() == "example.com  300s  A  93.184.216.34", proc.stdout

proc = run_query(lambda packet: make_response(packet, rcode=3))
assert proc.returncode == 1
assert "rcode 3" in proc.stdout

print("ok")
