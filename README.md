# net-from-scratch

Twenty small programs that rebuild the network stack one layer at a time:
sockets, HTTP/1.1, DNS, TLS. Each step runs on its own, and each one has a test
that starts it and talks to it over a real socket.

Python 3.8 or newer, standard library only. Chapters 17-20 also need `openssl`.

## Why

You can read about the TCP handshake for years and still not know why
`recv(1024)` sometimes returns half a message. Every step here is a program you
run in two terminals, so the thing you are reading about is the thing that just
failed.

## Quickstart

```console
$ python steps/01-echo-server/echo_server.py
listening on 127.0.0.1:8000
```

In a second terminal:

```console
$ python steps/01-echo-server/client.py
connected to 127.0.0.1:8000, ctrl-d to quit
hello
hello
```

For the HTTP chapters:

```console
$ python steps/13-real-page/app_server.py
$ curl http://127.0.0.1:8000/
```

## The steps

| # | Step | What you build |
| --- | --- | --- |
| 01 | `echo-server` | a TCP socket that echoes bytes |
| 02 | `many-clients` | one thread per connection |
| 03 | `framing` | length-prefixed messages over a byte stream |
| 04 | `kv-protocol` | SET/GET/DEL over a line protocol |
| 05 | `http-request` | parse a request line and headers |
| 06 | `http-response` | status line, headers, body |
| 07 | `static-files` | map URLs to files with content types |
| 08 | `path-safety` | stop `..` from escaping the document root |
| 09 | `keep-alive` | many requests on one connection |
| 10 | `chunked` | chunked transfer encoding |
| 11 | `request-bodies` | Content-Length, JSON, 400s and 411s |
| 12 | `selectors` | one thread, many connections |
| 13 | `real-page` | HTML, CSS, JavaScript, and a JSON endpoint |
| 14 | `dns-query` | build and parse DNS packets by hand |
| 15 | `dns-server` | a stub resolver over UDP |
| 16 | `dns-over-tcp` | the same message with a length prefix |
| 17 | `tls-handshake` | wrap a socket in TLS |
| 18 | `https-server` | the page from step 13 over TLS |
| 19 | `certificates` | read the certificate chain |
| 20 | `mini-curl` | DNS + TCP + TLS + HTTP in one command |

## Running the tests

```console
$ python tools/make_cert.py    # once, for chapters 17-20
$ python tools/check.py
PASS  01-echo-server  (0.0s)
...
20/20 steps pass
```

Each `steps/*/test.py` starts the server with `--port 0`, reads the port it
printed, talks to it over a socket, and asserts on what came back. No mocking:
the tests use the same bytes a client would.

Without `openssl` the four TLS chapters cannot run. They exit 77, `check.py`
prints `SKIP` for them, and the summary reports the skips instead of counting
them as passes:

```console
$ python tools/check.py
...
SKIP  17-tls-handshake  (0.0s)
      skipped: no certificates (run tools/make_cert.py)
...
16/20 steps pass, 4 skipped
```

`python tools/test_check.py` covers the summary logic itself. CI runs both on
Python 3.8, 3.11, and 3.13.

## What this is not

- Not a production server. No timeouts, no connection limits, no logging worth
  keeping. Do not put this on the internet.
- Not a theory course. It is the code, with the minimum explanation needed to
  see why the code is shaped that way.
- Not a curl replacement. Step 20 does one method, no cookies, no HTTP/2.
- Not complete. HTTP/2, QUIC, IPv6, and DNS over HTTPS are all missing, and each
  of them is a repository of its own.

## Requirements

- Python 3.8 or newer.
- `openssl` for chapters 17-20. The certificate generator shells out to it; the
  tests skip those steps if it is missing.

Everything else is the standard library.

## Layout

```
steps/01-echo-server/
├── README.md        what and why
├── echo_server.py   the program
├── client.py        the other terminal
└── test.py          starts it, talks to it, asserts

tools/
├── check.py         runs every test
├── make_cert.py     makes .certs/ (gitignored)
└── testkit.py       starts a server and finds its port
```

Every server prints the port it actually bound, which is why `--port 0` works
and why the tests never race for a fixed port.

## License

MIT. See `LICENSE`.
