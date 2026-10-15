"""APIキーの取得。値は表示・記録しない。環境変数 → macOSキーチェーンの順で探す。"""
import os
import shutil
import subprocess

KEYCHAIN_SERVICE = "leakwatch-jp"


def get_secret(name: str) -> str | None:
    val = os.environ.get(name)
    if val:
        return val
    if shutil.which("security"):
        try:
            r = subprocess.run(
                ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-a", name, "-w"],
                capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None
