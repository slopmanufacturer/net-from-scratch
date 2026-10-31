#!/usr/bin/env python3
"""Run every steps/*/test.py and print a summary.

A test that exits 77 did not run: it skipped for a missing prerequisite. Skips
are reported separately and are never counted as passes.
"""

import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PYTHON = sys.executable
TIMEOUT = 120
SKIP = 77

sys.path.insert(0, str(ROOT / "tools"))
import make_cert  # noqa: E402


def summarize(total, failed, skipped):
    passed = total - len(failed) - len(skipped)
    line = f"{passed}/{total} steps pass"
    if skipped:
        line += f", {len(skipped)} skipped"
    if failed:
        line += f", {len(failed)} failed"
    return line


def main():
    tests = sorted(ROOT.glob("steps/*/test.py"))
    if not tests:
        print("no tests found")
        return 1

    make_cert.ensure()

    failed = []
    skipped = []
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
            code = proc.returncode
            output = (proc.stdout + proc.stderr).strip()
        except subprocess.TimeoutExpired:
            code = 1
            output = f"timed out after {TIMEOUT}s"

        elapsed = time.time() - started
        if code == 0:
            print(f"PASS  {name}  ({elapsed:.1f}s)")
        elif code == SKIP:
            print(f"SKIP  {name}  ({elapsed:.1f}s)")
            for line in output.splitlines()[:2]:
                print("      " + line)
            skipped.append(name)
        else:
            print(f"FAIL  {name}")
            for line in output.splitlines()[-12:]:
                print("      " + line)
            failed.append(name)

    print("\n" + summarize(len(tests), failed, skipped))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
