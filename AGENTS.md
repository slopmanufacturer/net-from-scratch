# AGENTS.md

## What this is

Twenty small programs that rebuild the network stack in order: sockets, framing,
HTTP/1.1, DNS, TLS. Each step is a standalone script with a `README.md` that
explains the idea and a `test.py` that starts the program on a real socket and
asserts on the bytes. Nothing is mocked and nothing is a library.

## Entry points

| Question | Where |
| --- | --- |
| What does step N teach? | `steps/<NN-name>/README.md` |
| How does a step's test work? | `steps/<NN-name>/test.py`, using `tools/testkit.py` |
| How do I run everything? | `python3 tools/check.py` |
| How do I make the TLS certificates? | `python3 tools/make_cert.py` |
| Where is the skip logic? | `tools/check.py` + exit code 77 |

## Invariants

1. A test that cannot run exits **77**. It never exits 0. `check.py` maps 77 to
   `SKIP` and keeps it out of the pass count.
2. `check.py` exits 1 if and only if a step failed. Skips do not fail the run.
3. Every test that starts a server does it through `testkit.start_server`, which
   passes `--port 0` and reads the port the server printed. Never hard-code a
   port in a test. (`steps/14-dns-query` has no server; it tests the packet
   builder and parser directly.)
4. Every server prints a `listening on <host>:<port>` line, and it must keep
   doing that: `testkit` parses it and fails the test if it never appears.
5. Standard library only, Python 3.8 syntax. No third-party imports, no
   `match` statements, no `X | Y` annotations, no `removeprefix`.
6. Each step is self-contained: it may import from `tools/` or a sibling step,
   but it must run on its own from its own directory.

## Commands

```bash
python3 tools/make_cert.py      # once; writes .certs/ (gitignored)
python3 tools/check.py          # every step, with SKIP/FAIL/PASS
python3 tools/test_check.py     # the summary logic
```

The one command that proves the work: `python3 tools/check.py`.

## Sharp edges

- **Exit 0 from a test means it actually ran.** If you add a prerequisite check,
  exit 77, or the suite will claim a pass for a chapter that never executed.
  That was F1 in `AUDIT.md`.
- **A partially-skipped test is a skip.** `steps/20-mini-curl` runs its HTTP half
  and then exits 77 when the certificates are missing, because the HTTPS half
  did not run.
- **`.certs/` is generated, gitignored, and not secret.** Never commit it;
  `make_cert.py` recreates it. `check.py` calls `ensure()` itself, so a fresh
  clone works without a separate step as long as `openssl` exists.
- **`make_cert.ensure()` returns False when `openssl` is missing** and prints a
  notice. `check.py` deliberately does not abort on that: the non-TLS steps
  should still run.
- **Tests bind to `127.0.0.1` and real ports.** They are not hermetic against a
  hostile network config, but they never use the internet.
- **The certificate has `subjectAltName` for `localhost` and `127.0.0.1`.**
  Removing either breaks step 20's verification path.

## Definition of done

- [ ] `python3 tools/check.py` — no FAIL lines.
- [ ] `python3 tools/test_check.py` passes.
- [ ] A new step has `README.md`, the program, and `test.py`.
- [ ] A new step is added to the table in `README.md`.
- [ ] Skips still exit 77 and are visible in the summary.

## Do not touch

- `LICENSE`.
- The step order and directory names; the README table and cross-step imports
  depend on them.
- `.certs/` (generated).
- The teaching tone of the step READMEs. They explain why the code is shaped
  that way; do not turn them into API docs.
