"""漏洩情報源（差し替え可能）。自前のダークウェブ巡回は行わない。"""
from .base import Breach, BreachSource
from .hibp import HIBPSource
from .mock import MockSource
from .paid import FlareSource, SpyCloudSource

REGISTRY = {"hibp": HIBPSource, "mock": MockSource, "spycloud": SpyCloudSource, "flare": FlareSource}


def get_source(name: str) -> BreachSource:
    if name not in REGISTRY:
        raise ValueError(f"不明な情報源: {name}（使えるもの: {', '.join(REGISTRY)}）")
    return REGISTRY[name]()
