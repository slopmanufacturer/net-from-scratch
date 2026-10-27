# 04 — A line protocol

Before HTTP, most protocols were text commands separated by newlines. This is
one of them: a key-value store you talk to over TCP.

```
SET name ada        ->  OK
GET name            ->  VALUE ada
GET missing         ->  NONE
DEL name            ->  OK
QUIT                ->  BYE
```

## Run it

```console
$ python kv_server.py
$ python kv_client.py
SET name ada
OK
GET name
VALUE ada
```

## What to notice

- The newline is the frame. That works because values cannot contain newlines;
  the moment they can, you need escaping or a length prefix.
- `read_line` keeps a buffer between calls. TCP will happily hand you two
  commands in one `recv`, and the buffer is what makes that harmless.
- The store lives in the server process, behind a lock. Two clients share it,
  which is the whole point of a server.
- `split(" ", 2)` is deliberate: the value may contain spaces, so only the first
  two separators matter.

## Test

```console
$ python test.py
ok
```
