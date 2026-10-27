# 15 — A DNS server

A resolver that only knows a few names is called a stub. This one answers from a
dictionary, which is enough to see the response format from the other side.

```python
ZONE = {
    "example.com": "93.184.216.34",
    "api.example.com": "93.184.216.35",
    "www.example.com": "93.184.216.34",
    "localhost.test": "127.0.0.1",
}
```

## Run it

```console
$ python dns_server.py
listening on 127.0.0.1:5353
```

In a second terminal, using the client from step 14:

```console
$ python ../14-dns-query/dns_query.py api.example.com --server 127.0.0.1 --port 5353
api.example.com  60s  A  93.184.216.35
```

If you have `dig`:

```console
$ dig @127.0.0.1 -p 5353 example.com +short
93.184.216.34
```

## What to notice

- The response copies the question section verbatim and appends one answer.
- The answer name is a pointer to offset 12 (`\xc0\x0c`), not a repeated string.
  It saves bytes and it is why DNS parsers are careful about loops.
- rcode 3 is NXDOMAIN. This server returns it for any name not in the zone,
  including names that exist in the real world.
- The TTL is 60 seconds here. Step 14's real answer used 300. Whoever receives
  the answer is allowed to cache it for that long.
- A real resolver walks the delegation chain from the root servers. This one
  cheats, and that is the point: the wire format is the interesting part.

## Test

```console
$ python test.py
ok
```
