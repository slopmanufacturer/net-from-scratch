"""Helpers shared by the step tests. Not part of the teaching material."""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PYTHON = sys.executable


def start_server(script, *args, timeout=10):
    """Start a server with --port 0 and return (process, port).

    Servers announce themselves with a line like "listening on 127.0.0.1:53211";
    the port is read from that line rather than guessed.
    """
    cmd = [PYTHON, str(script), "--port", "0", *args]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
    )
    while True:
        line = proc.stdout.readline()
        if line:
            match = re.search(r"listening on \S+:(\d+)", line)
            if match:
                return proc, int(match.group(1))
            continue
        if proc.poll() is not None:
            raise RuntimeError(f"server exited before listening:\n{proc.stderr.read()}")
        proc.kill()
        raise RuntimeError("server closed stdout before listening")


def stop(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
