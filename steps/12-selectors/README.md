# 12 — One thread, many connections

Step 02 used a thread per client. This step uses one thread for all of them:
make every socket non-blocking, ask the kernel which ones are ready, handle
those.

## Run it

```console
$ python select_server.py
$ curl -s http://127.0.0.1:8000/a
path=/a
```

Open three clients at once; one thread serves all of them.

## What to notice

- `select()` tells you a socket is *ready*, not that a read will return
  everything. Every handler still has to deal with partial data.
- `setblocking(False)` turns a stall into `BlockingIOError`. That exception is
  not an error, it is "try later".
- `selector.modify` is how a connection moves from "waiting for a request" to
  "waiting to drain a response". One socket, two interests.
- `on_write` keeps the unsent tail of `outbuf`. `send()` returns how many bytes
  it took, and it is allowed to take fewer than you offered.
- This is the shape of every event loop you have used: nginx, Node, asyncio,
  Tokio. The differences are in the details, not the idea.

## Test

```console
$ python test.py
ok
```
