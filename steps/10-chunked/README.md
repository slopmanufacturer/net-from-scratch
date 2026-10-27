# 10 — Chunked transfer encoding

`Content-Length` requires knowing the size before the first byte leaves. That
does not work for a generated report, a proxy, or a response that is still being
computed.

Chunked encoding sends the body as a series of pieces:

```
7\r\n
one \r\n
7\r\n
two \r\n
9\r\n
three\n\r\n
0\r\n
\r\n
```

Each chunk is `hex size`, `CRLF`, the bytes, `CRLF`. A zero-length chunk ends the
body.

## Run it

```console
$ python chunked_server.py
$ python chunked_client.py
Transfer-Encoding: chunked
body: one two three
```

## What to notice

- There is no `Content-Length`. The end of the body is the `0` chunk, not EOF.
- The size is hex, and it counts bytes, not characters.
- A chunk can be split across TCP reads; the parser has to buffer, exactly like
  step 03.
- Real chunked responses can carry trailers after the zero chunk. This server
  does not, so the client reads one empty line and stops.
- HTTP/2 dropped chunked encoding: it has its own frame lengths.

## Test

```console
$ python test.py
ok
```
