# 07 — Static files

Now the server reads from disk. `/` maps to `site/index.html`, everything else
maps to a file under `site/`.

## Run it

```console
$ python static_server.py
$ curl -i http://127.0.0.1:8000/
$ curl -i http://127.0.0.1:8000/style.css
$ curl -i http://127.0.0.1:8000/missing
```

## What to notice

- Read files as bytes and write bytes. Decoding a PNG to text and back is how
  people break their images.
- The `Content-Type` tells the browser how to interpret the bytes. `text/plain`
  with HTML in it renders as source; `text/html` renders as a page.
- `Path.suffix` is enough for a toy. Real servers sniff the first bytes and fall
  back to the `Accept` header.
- This server is one `..` away from serving your SSH keys. That is step 08.

## Test

```console
$ python test.py
ok
```
