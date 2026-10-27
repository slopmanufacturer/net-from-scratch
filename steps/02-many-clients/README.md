# 02 — Many clients

Step 01 accepts one connection and then exits. Real servers keep accepting.
The simplest fix is a thread per connection.

## Run it

```console
$ python threaded_server.py
listening on 127.0.0.1:8000
client 1 from 127.0.0.1:53120
client 2 from 127.0.0.1:53121
```

Open three terminals and run `python ../01-echo-server/client.py` in two of
them. Both stay connected at once.

## What to notice

- `accept()` returns a socket per client. The listening socket is only a door.
- A thread blocked in `recv()` costs almost nothing. This is why thread-per-
  connection servers survive a few thousand idle clients, and why they fall over
  at a few tens of thousands.
- The GIL does not matter here: the threads are waiting on the kernel, not on
  Python bytecode.
- Step 12 does the same job with one thread and `selectors`.

## Test

```console
$ python test.py
ok
```
