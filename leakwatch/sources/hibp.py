import json
import time
import urllib.error
import urllib.parse
import urllib.request

from .. import __version__
from ..secrets import get_secret
from .base import Breach, BreachSource

API = "https://haveibeenpwned.com/api/v3/breachedaccount/"


class HIBPSource(BreachSource):
    """Have I Been Pwned v3 API。キーは HIBP_API_KEY（環境変数かキーチェーン）。"""
    name = "hibp"

    def __init__(self, opener=None):
        self._open = opener or urllib.request.urlopen

    def available(self) -> bool:
        return get_secret("HIBP_API_KEY") is not None

    def check_email(self, email: str) -> list[Breach]:
        key = get_secret("HIBP_API_KEY")
        if not key:
            raise RuntimeError("HIBP_API_KEY が見つかりません（README参照。--source mock で試せます）")
        url = API + urllib.parse.quote(email) + "?truncateResponse=false"
        req = urllib.request.Request(url, headers={
            "hibp-api-key": key,
            "user-agent": f"leakwatch-jp/{__version__}",
        })
        for attempt in range(3):
            try:
                with self._open(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return []
                if e.code == 429 and attempt < 2:
                    time.sleep(int(e.headers.get("retry-after", "2")) + 1)
                    continue
                if e.code == 401:
                    raise RuntimeError("HIBP APIキーが無効です") from None
                raise RuntimeError(f"HIBP APIエラー: HTTP {e.code}") from None
        return [
            Breach(
                name=b.get("Name", ""), title=b.get("Title", ""), domain=b.get("Domain", ""),
                breach_date=b.get("BreachDate", ""), data_classes=list(b.get("DataClasses", [])),
                is_verified=bool(b.get("IsVerified", True)), source=self.name,
            )
            for b in data
        ]
