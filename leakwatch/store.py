"""進捗のローカル保存。~/.leakwatch/state.json（権限600）。外部送信しない。"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def default_path() -> Path:
    return Path(os.environ.get("LEAKWATCH_HOME", Path.home() / ".leakwatch")) / "state.json"


class Store:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else default_path()
        self.data = {"emails": [], "findings": {}}
        if self.path.exists():
            self.data = json.loads(self.path.read_text("utf-8"))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        tmp = self.path.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def add_email(self, email: str):
        email = email.strip().lower()
        if email not in self.data["emails"]:
            self.data["emails"].append(email)

    def remove_email(self, email: str):
        email = email.strip().lower()
        self.data["emails"] = [e for e in self.data["emails"] if e != email]
        self.data["findings"] = {k: v for k, v in self.data["findings"].items() if v["email"] != email}

    def upsert_finding(self, email, breach, severity, actions):
        fid = f"{email}:{breach.name}"
        prev = self.data["findings"].get(fid, {})
        self.data["findings"][fid] = {
            "email": email, "breach": breach.name, "title": breach.title, "domain": breach.domain,
            "breach_date": breach.breach_date, "data_classes": breach.data_classes,
            "severity": severity, "actions": actions, "source": breach.source,
            "status": prev.get("status", "open"), "updated": prev.get("updated"),
        }
        return fid

    def set_status(self, fid: str, status: str):
        if fid not in self.data["findings"]:
            raise KeyError(fid)
        self.data["findings"][fid]["status"] = status
        self.data["findings"][fid]["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
