"""ローカルのOpenAI互換API（任意）。LEAKWATCH_LLM_URL / LEAKWATCH_LLM_MODEL。未設定ならLLMなしで動く。"""
import json
import os
import urllib.request


class Client:
    def __init__(self, base_url=None, model=None):
        self.base_url = (base_url or os.environ.get("LEAKWATCH_LLM_URL", "")).rstrip("/")
        self.model = model or os.environ.get("LEAKWATCH_LLM_MODEL", "glm-5.3-flash")

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def chat(self, system: str, user: str) -> str | None:
        if not self.enabled:
            return None
        body = json.dumps({"model": self.model, "temperature": 0,
                           "messages": [{"role": "system", "content": system},
                                        {"role": "user", "content": user}]}).encode()
        req = urllib.request.Request(self.base_url + "/chat/completions", data=body,
                                     headers={"content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())["choices"][0]["message"]["content"]
        except Exception:
            return None
