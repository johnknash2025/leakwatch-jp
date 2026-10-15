import json
from importlib import resources


def load() -> list[dict]:
    text = resources.files("leakwatch").joinpath("data/playbooks.json").read_text("utf-8")
    return json.loads(text)["services"]


def find_for_domain(domain: str) -> dict | None:
    d = (domain or "").lower()
    for s in load():
        if any(d == m or d.endswith("." + m) for m in s["match_domains"]):
            return s
    return None


def get(service_id: str) -> dict | None:
    return next((s for s in load() if s["id"] == service_id), None)
