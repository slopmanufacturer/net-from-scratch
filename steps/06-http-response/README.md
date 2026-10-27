# 06 — Writing a response

The response has the same shape as the request: a status line, headers, a blank
line, then the body.

```
HTTP/1.1 200 OK\r\n
Content-Type: text/html; charset=utf-8\r\n
Content-Length: 120\r\n
Connection: close\r\n
\r\n
<!doctype html>...
```

## Run it

```console
$ python http_server.py
$ curl -i http://127.0.0.1:8000/
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 120
Connection: close

<!doctype html>
...
$ curl -i http://127.0.0.1:8000/nope
HTTP/1.1 404 Not Found
```

## What to notice

- The status line is `version code reason`. The reason phrase is for humans and
  clients ignore it; the number is the contract.
- `Content-Length` is the number of **bytes**, not characters. `len(body)` on a
  `bytes` object is correct; `len(text)` on a string is not, once there is a
  single non-ASCII character in it.
- With `Connection: close`, the client could technically read until EOF and
  ignore `Content-Length`. Do not build on that: keep-alive (step 09) removes
  the EOF.
- A 404 is a perfectly successful HTTP exchange. The status code is the message.

## Test

```console
$ python test.py
ok
```
