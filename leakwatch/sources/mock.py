from .base import Breach, BreachSource

_FIXTURES = {
    "pwned@example.com": [
        Breach("Adobe", "Adobe", "adobe.com", "2013-10-04",
               ["Email addresses", "Password hints", "Passwords", "Usernames"], True, "mock"),
        Breach("ExampleShop", "Example Shop", "shop.example", "2022-05-01",
               ["Email addresses", "Phone numbers", "Partial credit card data", "Physical addresses"], True, "mock"),
    ],
    "spam@example.com": [
        Breach("SpamList", "Spam List", "", "2019-01-01", ["Email addresses"], False, "mock"),
    ],
}


class MockSource(BreachSource):
    """キーなしで動作確認するためのモック。pwned@example.com / spam@example.com が漏洩あり。"""
    name = "mock"

    def check_email(self, email: str) -> list[Breach]:
        return list(_FIXTURES.get(email.lower(), []))
