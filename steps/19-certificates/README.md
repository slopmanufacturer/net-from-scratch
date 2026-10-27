# 19 — Reading a certificate

The handshake is a chain of signatures. The server sends its certificate; the
certificate is signed by a CA; the CA's certificate is signed by another CA, or
is a root the client already trusts.

## Run it

```console
$ python ../18-https-server/https_server.py
$ python inspect_cert.py
subject:
  commonName: localhost
issuer:
  commonName: net-from-scratch CA
subjectAltName:
  DNS: localhost
  IP Address: 127.0.0.1
valid from: ...
valid to:   ...
serial:     ...
```

Or with openssl:

```console
$ openssl s_client -connect localhost:8443 -CAfile ../.certs/ca.pem </dev/null 2>/dev/null | openssl x509 -noout -text
```

## What to notice

- `getpeercert()` returns a dict only after a *successful* verification. With
  `CERT_NONE` you get `{}`, because nothing was checked.
- The identity is in `subjectAltName`, not `commonName`. Browsers have ignored CN
  for years; a certificate with only a CN is rejected.
- The issuer here is your own CA. The client trusts it because you passed
  `cafile=`. A public site's chain ends at a root that ships with the OS.
- `notAfter` is the expiry. An expired certificate fails the same way a wrong
  name does, and the error message is just as unhelpful.
- A certificate is public. The private key is the secret, and it never leaves the
  server.

## Test

```console
$ python test.py
ok
```
