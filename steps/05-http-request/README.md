# 05 — Parsing a request

An HTTP/1.1 request is a request line, some headers, a blank line, and then
optionally a body.

```
GET /hello?x=1 HTTP/1.1\r\n
Host: localhost\r\n
User-Agent: curl/8.5.0\r\n
\r\n
```

That is the whole format. The `\r\n` is the line break; the empty line ends the
headers.

## Run it

```console
$ python request_server.py
$ curl -s http://127.0.0.1:8000/hello?x=1 -H 'X-Test: yes'
method: GET
path: /hello?x=1
version: HTTP/1.1
host: 127.0.0.1:8000
user-agent: curl/8.5.0
accept: */*
x-test: yes
```

## What to notice

- The read loop does not stop at the first `recv`. A request can arrive in
  fragments, and the only reliable end marker is `\r\n\r\n`.
- Header names are case-insensitive, so they are lowercased on the way in.
- `partition(":")` splits on the first colon only, which is what you want for
  values like `Accept: text/html;q=0.9`.
- `iso-8859-1` decodes any byte sequence without raising. HTTP headers are
  ASCII in practice, but a malformed request should not crash the parser.
- The bytes after `\r\n\r\n` are the start of the body. Step 11 uses them.

## Test

```console
$ python test.py
ok
```
