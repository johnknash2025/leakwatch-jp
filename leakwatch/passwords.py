"""Pwned Passwords（HIBP、無料・キー不要）。k-匿名性: SHA-1の先頭5文字だけを送る。
パスワード本体とハッシュ全体は送信・表示・保存しない。"""
import hashlib
import urllib.request

from . import __version__

API = "https://api.pwnedpasswords.com/range/"


def pwned_count(password: str, opener=None) -> int:
    h = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = h[:5], h[5:]
    req = urllib.request.Request(API + prefix, headers={
        "user-agent": f"leakwatch-jp/{__version__}", "add-padding": "true"})
    with (opener or urllib.request.urlopen)(req, timeout=20) as r:
        body = r.read().decode("utf-8")
    for line in body.splitlines():
        s, _, n = line.strip().partition(":")
        if s == suffix:
            return int(n)
    return 0
