# 20 — mini curl

Everything in this repository, in one file: resolve a name, open a socket, maybe
wrap it in TLS, send a request, read a response, handle chunked bodies, follow a
redirect.

## Run it

```console
$ python ../18-https-server/https_server.py
$ python mini_curl.py https://localhost:8443/
<!doctype html>
...
$ python mini_curl.py -i https://localhost:8443/api/time
HTTP/1.1 200 OK
content-type: application/json
content-length: 41
connection: close

{"time": "14:32:07", "epoch": 1750000000}
```

Plain HTTP and chunked responses work too:

```console
$ python ../10-chunked/chunked_server.py
$ python mini_curl.py http://127.0.0.1:8000/
one two three
```

## What to notice

- The URL parse is `urllib.parse`. The interesting part is the three transports
  stacked under it: DNS to find an address, TCP to reach the port, TLS to make
  the bytes private.
- `getaddrinfo` can return several addresses. The loop tries each one, which is
  what makes `localhost` work whether it resolves to `::1` or `127.0.0.1`.
- `read_response` has three ways to know where the body ends: `Content-Length`,
  a chunked terminator, or the server closing the connection. Real clients
  handle all three because real servers use all three.
- `-L` follows `Location`, up to five hops. Without a hop limit, a redirect loop
  is an infinite loop.
- The exit code follows the status: 0 for 2xx and 3xx, 1 for 4xx and 5xx. That
  is what makes a client scriptable.

## What it does not do

No POST, no cookies, no HTTP/2, no proxy support, no connection reuse. `curl`
has had thirty years and a lot of contributors.

## Test

```console
$ python test.py
ok
```
