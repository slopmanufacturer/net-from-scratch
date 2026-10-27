# 14 — DNS, by hand

DNS is a binary protocol over UDP. There is no HTTP here: you build a packet,
send it to port 53, and parse bytes back.

## The packet

```
+-- header (12 bytes) --+-- question --+-- answers --+
| id  flags  qd an ns ar |  name  type  |  ...        |
```

A name is a sequence of length-prefixed labels:

```
www.example.com  ->  03 77 77 77  07 65 78 61 6d 70 6c 65  03 63 6f 6d  00
                     "www"        "example"                 "com"        end
```

## Run it

```console
$ python dns_query.py example.com
example.com  194s  A  104.20.23.154
```

The address and TTL change with every resolver and every cache. The shape of the
line does not.

Against your own server from step 15:

```console
$ python dns_query.py api.example.com --server 127.0.0.1 --port 5353
```

`--show-packet` prints the query in hex so you can compare it with the diagram.

## What to notice

- The header is six big-endian 16-bit fields. `struct.pack("!HHHHHH", ...)` is
  the whole thing.
- `0x0100` is the flags word: recursion desired, everything else zero.
- The answer name is usually a pointer, not a repeated string. `0xC00C` means
  "the name at offset 12", which is the question name. That is why the parser
  has to follow pointers.
- TTL is in seconds. It is the only caching instruction in the protocol.
- A response with rcode 3 is NXDOMAIN: the name does not exist. A response with
  zero answers but rcode 0 means the name exists and has no A record.
- UDP has no delivery guarantee. A lost packet is a timeout, and the resolver
  retries. That is why the client takes `--timeout`.

## Test

```console
$ python test.py
ok
```
