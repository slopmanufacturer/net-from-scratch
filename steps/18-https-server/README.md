# 18 — HTTPS

The server from step 13, with one extra layer:

```python
tls = context.wrap_socket(conn, server_side=True)
```

Everything after that line is the HTTP code you already wrote.

## Run it

```console
$ python tools/make_cert.py     # once, from the repo root
$ python https_server.py
listening on 127.0.0.1:8443
$ python https_client.py
HTTP/1.1 200 OK
346 bytes of body
<!doctype html>
...
```

Or with curl:

```console
$ curl --cacert .certs/ca.pem https://localhost:8443/
$ curl -k https://localhost:8443/          # skip verification, for comparison
```

## What to notice

- `--cacert` is the whole difference between "works" and `SSL certificate
  problem: self-signed certificate`. The browser is not being difficult; it has
  no reason to trust your CA.
- The certificate is for `localhost`, so `https://127.0.0.1:8443/` only works
  because the certificate also lists `IP:127.0.0.1` in its SAN. Drop that and
  the IP form fails while the name form keeps working.
- The handshake happens before your HTTP parser sees a byte. A failed handshake
  never reaches `read_request`.
- The TLS wrap is per connection. `accept()` still returns a plain socket; it
  becomes a TLS socket only after `wrap_socket`.

## Test

```console
$ python test.py
ok
```
