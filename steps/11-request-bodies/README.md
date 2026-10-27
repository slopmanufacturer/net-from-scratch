# 11 — Request bodies

The header block tells you how many body bytes follow. If you ignore
`Content-Length`, you read the body as if it were the next request.

## Run it

```console
$ python json_server.py
$ curl -s -X POST http://127.0.0.1:8000/echo \
    -H 'Content-Type: application/json' \
    -d '{"name": "ada"}'
{"hello": "ada", "bytes": 16}
```

## What to notice

- `leftover` from the header read is already part of the body. A request can
  arrive header and body in the same packet.
- `read_exactly` loops, because a body can arrive in as many pieces as TCP feels
  like. This is step 03 again, with the length in a header instead of a prefix.
- `411 Length Required` exists precisely for this case. HTTP/1.1 allows
  `Transfer-Encoding: chunked` instead of a length, which is step 10 in reverse.
- Parsing JSON from an untrusted body can raise; a 400 is cheaper than a
  traceback and a dropped connection.

## Test

```console
$ python test.py
ok
```
