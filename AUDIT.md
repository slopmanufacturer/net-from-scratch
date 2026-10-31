# Audit — 2026-10-31

Scope: `tools/`, every `steps/*/test.py`, README, CI.
Baseline before any change:

```
$ python3 tools/make_cert.py
wrote .certs/ (ca.pem, server.pem, server.key)
$ python3 tools/check.py
PASS  01-echo-server  (0.0s)
...
20/20 steps pass
```

| # | Finding | Severity | Status |
| --- | --- | --- | --- |
| F1 | A skipped step is reported as PASS and counted in "20/20 steps pass" | Medium | fixed, `tools/test_check.py` |
| F2 | Nothing runs the 20 tests on push | Medium | fixed |
| F3 | No AGENTS.md | Low | fixed |

## F1 — Four chapters can not run and the suite still says 20/20 (Medium)

**Claim:** "Each step runs on its own, and each one has a test that starts it
and talks to it over a real socket", and the summary "20/20 steps pass".
**Evidence:** with `openssl` off `PATH` and `.certs/` absent:

```
$ PATH=/tmp/emptybin /usr/bin/python3 tools/check.py
...
PASS  17-tls-handshake  (0.0s)
PASS  18-https-server  (0.0s)
PASS  19-certificates  (0.0s)
PASS  20-mini-curl  (0.7s)

20/20 steps pass
exit 0
```

None of the four TLS chapters ran. `steps/17,18,19` printed
"skipped: no certificates" and exited 0; `steps/20-mini-curl` silently skipped
its whole HTTPS half, including the redirect test, and exited 0.
**Cause:** a skip was signalled with the same exit code as a pass, and
`check.py` only distinguishes `0` from everything else.
**Fix:** a skip exits 77. `check.py` prints `SKIP` with the reason and counts
skips separately; `summarize()` no longer counts them as passes. Step 20 still
runs its HTTP half and then exits 77 with "skipped the HTTPS half".
**Status:** fixed. Same command now reports:

```
SKIP  17-tls-handshake  (0.0s)
SKIP  18-https-server  (0.0s)
SKIP  19-certificates  (0.0s)
SKIP  20-mini-curl  (0.7s)
16/20 steps pass, 4 skipped
```

`tools/test_check.py` covers `summarize()`: all-pass, skips, and failures.

## F2 — No CI (Medium)

Twenty tests, a certificate generator, and nothing ran them on push. A
regression in any step could land on `main` unnoticed.
**Fix:** `.github/workflows/checks.yml` runs `tools/test_check.py` and
`tools/check.py` on Python 3.8, 3.11, and 3.13. The 3.8 job is also the proof
for the "Python 3.8 or newer" claim, which was previously unverified.

## F3 — No AGENTS.md (Low)

Nothing recorded that a skip must not look like a pass, or that every test
starts its server with `--port 0`. **Status:** fixed.

## Verified, no finding

- `20/20 steps pass` with `openssl` present.
- Standard library only: every import in `steps/` and `tools/` is stdlib or a
  sibling module (`dns_query`, `framed_server`, `testkit`, `make_cert`).
- Python 3.8 claim: no `match` statements, no `X | Y` annotations, no
  `removeprefix`, no `dict[...]` at runtime. CI now proves it rather than
  asserting it.
- Every test that needs a server starts it through `testkit.start_server`, which
  passes `--port 0` and parses the port from the `listening on <host>:<port>`
  line. `steps/14-dns-query` is the one test with no server: it exercises the
  packet builder and parser directly.
