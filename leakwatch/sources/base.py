from dataclasses import dataclass, field


@dataclass
class Breach:
    name: str
    title: str
    domain: str
    breach_date: str
    data_classes: list[str] = field(default_factory=list)
    is_verified: bool = True
    source: str = ""


class BreachSource:
    name = "base"

    def available(self) -> bool:
        return True

    def check_email(self, email: str) -> list[Breach]:
        raise NotImplementedError
