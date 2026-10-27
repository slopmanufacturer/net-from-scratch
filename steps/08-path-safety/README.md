# 08 — Path traversal

Step 07 joins the URL to the root and opens whatever comes out:

```python
target = root / path.lstrip("/")
```

Ask for `/../secret.txt` and you get `site/../secret.txt`. Ask for
`/%2e%2e/secret.txt` and the URL decoder turns it into the same thing.

## The fix

Resolve the path, then check that the result is still inside the root:

```python
root = root.resolve()
target = (root / unquote(path).lstrip("/")).resolve()
if target != root and root not in target.parents:
    return None   # 403
```

## Run it

```console
$ python safe_server.py
$ curl -i http://127.0.0.1:8000/sub/page.html
HTTP/1.1 200 OK
$ curl -i --path-as-is http://127.0.0.1:8000/../secret.txt
HTTP/1.1 403 Forbidden
$ curl -i http://127.0.0.1:8000/%2e%2e/secret.txt
HTTP/1.1 403 Forbidden
```

`--path-as-is` matters: curl normalizes `..` before sending unless you tell it
not to.

## What to notice

- Checking `path.startswith("..")` is not enough. `sub/../../secret.txt` starts
  with `sub`, and `/./../secret.txt` starts with `/`.
- `resolve()` collapses `.`, `..`, and symlinks. Compare the result, not the
  string you started with.
- Decode first, then resolve. Doing it in the other order lets `%2e%2e` slip
  through.
- Real servers also reject null bytes and overlong paths. This one does not, and
  that is fine for a teaching server.

## Test

```console
$ python test.py
ok
```
