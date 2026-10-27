#!/usr/bin/env python3
"""Run every steps/*/test.py and print a summary."""

import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PYTHON = sys.executable
TIMEOUT = 120

sys.path.insert(0, str(ROOT / "tools"))
import make_cert  # noqa: E402


def main():
    tests = sorted(ROOT.glob("steps/*/test.py"))
    if not tests:
        print("no tests found")
        return 1

    make_cert.ensure()

    failed = []
    for test in tests:
        name = test.parent.name
        started = time.time()
        try:
            proc = subprocess.run(
                [PYTHON, str(test)],
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
                cwd=test.parent,
            )
            ok = proc.returncode == 0
            output = (proc.stdout + proc.stderr).strip()
        except subprocess.TimeoutExpired:
            ok = False
            output = f"timed out after {TIMEOUT}s"

        elapsed = time.time() - started
        if ok:
            print(f"PASS  {name}  ({elapsed:.1f}s)")
        else:
            print(f"FAIL  {name}")
            for line in output.splitlines()[-12:]:
                print("      " + line)
            failed.append(name)

    print(f"\n{len(tests) - len(failed)}/{len(tests)} steps pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
