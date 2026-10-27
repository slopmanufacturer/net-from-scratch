# 01 — A socket is a file

A TCP connection is a stream of bytes between two ports. Four calls set it up:
`socket()`, `bind()`, `listen()`, `accept()`. After that it is `recv()` and
`sendall()`.

## Run it

```console
$ python echo_server.py
listening on 127.0.0.1:8000
```

In a second terminal:

```console
$ python client.py
connected to 127.0.0.1:8000, ctrl-d to quit
hello
hello
```

## What to notice

- `listen()` does not accept anything. It marks the socket as willing to queue
  connections. `accept()` returns a *new* socket for one client.
- `recv(1024)` returns up to 1024 bytes. It is not a message, a line, or a
  request. Step 03 is about what that means.
- The server handles exactly one connection and then exits. Step 02 fixes that.
- The port is printed from `getsockname()`, not from the variable you passed in.
  That matters when you ask the OS to pick a port with `--port 0`.

## Test

```console
$ python test.py
ok
```
