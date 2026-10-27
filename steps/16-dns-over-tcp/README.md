# 16 — DNS over TCP

DNS runs on UDP because most queries are one packet in, one packet out. It also
runs on TCP, for responses that do not fit in 512 bytes, for zone transfers, and
increasingly for privacy work.

The message is byte-for-byte the same. Only the transport and the framing
change.

```
TCP:  +--------+-------------------------+
      | 2 byte |  DNS message            |
      | length |                         |
      +--------+-------------------------+
```

## Run it

```console
$ python tcp_server.py
listening on 127.0.0.1:5353
$ python tcp_query.py example.com
example.com  60s  A  93.184.216.34
```

If you have `dig`:

```console
$ dig @127.0.0.1 -p 5353 +tcp example.com +short
93.184.216.34
```

## What to notice

- The two-byte length is step 03 again. DNS over UDP gets message boundaries from
  the datagram; TCP does not, so the protocol has to add them.
- The server keeps the connection open and answers more than one query on it.
  The `while` loop is the same keep-alive idea as step 09.
- Nothing about the DNS message changed. That is the point of layering: a
  transport swap should not touch the parser.
- In the real world, a truncated UDP answer sets the TC bit and the client
  retries over TCP. This toy never truncates, because its answers are small.

## Test

```console
$ python test.py
ok
```
