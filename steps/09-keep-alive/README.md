# 09 — Keep-alive

Opening a TCP connection costs a handshake, a slow-start ramp, and (with TLS) a
certificate exchange. HTTP/1.1 keeps the connection open and sends another
request on it.

```
GET /a HTTP/1.1        ->  200, Connection: keep-alive
GET /b HTTP/1.1        ->  200, Connection: keep-alive
GET /c HTTP/1.1        ->  200, Connection: close
```

## Run it

```console
$ python keepalive_server.py
$ curl -v http://127.0.0.1:8000/a http://127.0.0.1:8000/b
```

curl reuses the connection when it can. Watch for `Re-using existing
connection` in the verbose output.

## What to notice

- HTTP/1.1 defaults to keep-alive. HTTP/1.0 defaults to close unless the client
  sends `Connection: keep-alive`.
- The read loop now has to carry a buffer between requests. Two pipelined
  requests can arrive in one packet, and the second one is sitting in
  `leftover`.
- Pipelining is legal but rare; browsers do not use it, because a slow response
  blocks every request behind it. That is head-of-line blocking, and it is what
  HTTP/2 and HTTP/3 spend most of their design budget on.
- A real server needs an idle timeout, otherwise every abandoned connection
  holds a thread forever.

## Test

```console
$ python test.py
ok
```
