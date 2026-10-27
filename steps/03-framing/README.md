# 03 — TCP is a byte stream

This is the step that bites everyone once.

```python
sock.sendall(b"alpha")
sock.sendall(b"beta")
```

The receiver is not promised two `recv()` calls of five and four bytes. It is
promised nine bytes, in order. They can arrive as `alpha` + `beta`, as
`alph` + `a` + `bet` + `a`, or all at once with the next message.

## The fix

Put a length in front of every message:

```
+--------+-------------------+
| 4 byte |  payload          |
| length |                   |
+--------+-------------------+
```

`send_message` writes the length and payload with one `sendall`. `recv_message`
reads exactly four bytes, learns the size, then reads exactly that many.

## Run it

```console
$ python framed_server.py
$ python framed_client.py
server: alpha
server: beta
server: gamma
echo: ONE TWO
```

The server sends all three messages in a single `sendall`. The client still gets
three separate messages, because the framing says where each one ends.

## What to notice

- `recv(1024)` is not `read(1024)`. There is no file position and no EOF marker
  until the peer closes.
- `recv_exactly` loops. A single `recv` can return short for reasons that have
  nothing to do with your code.
- Every protocol you have used has a framing rule: HTTP uses `Content-Length`
  and chunked encoding, DNS over TCP uses a two-byte length, Redis uses
  `\r\n`-terminated lines.

## Test

```console
$ python test.py
ok
```
