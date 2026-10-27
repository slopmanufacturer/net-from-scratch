# 13 — A real page

Everything so far was `curl`. This step is the same server with a page a browser
can load: HTML, CSS, JavaScript, and a JSON endpoint the JavaScript calls.

## Run it

```console
$ python app_server.py
```

Open <http://127.0.0.1:8000/>. The page asks `/api/time` for the server clock.

## What to notice

- The browser makes four requests for one page: `/`, `/style.css`, `/app.js`,
  and then `/api/time` once the JavaScript runs. Watch the server's terminal.
- The API response is JSON with `Content-Type: application/json`. If you send
  `text/html`, `response.json()` fails.
- `Connection: close` per request is why a browser opens several connections.
  Real servers keep them open, which is step 09.
- The path check from step 08 is still here. Serving a page does not make the
  traversal problem go away.

## Test

```console
$ python test.py
ok
```
