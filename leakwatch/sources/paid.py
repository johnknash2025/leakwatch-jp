"""有料API（キーを持つ人だけ有効）。MVPでは口のみ。"""
from ..secrets import get_secret
from .base import BreachSource


class _PaidSource(BreachSource):
    key_name = ""

    def available(self) -> bool:
        return get_secret(self.key_name) is not None

    def check_email(self, email):
        raise NotImplementedError(f"{self.name} 連携は未実装です（MVPでは口のみ）")


class SpyCloudSource(_PaidSource):
    name = "spycloud"
    key_name = "SPYCLOUD_API_KEY"


class FlareSource(_PaidSource):
    name = "flare"
    key_name = "FLARE_API_KEY"
