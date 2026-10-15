"""漏洩項目（HIBPのDataClasses）から深刻さを判定する。"""
from .sources.base import Breach

LEVELS = ["low", "medium", "high", "critical"]
LABEL_JA = {"low": "低", "medium": "中", "high": "高", "critical": "緊急"}

CRITICAL = {"passwords", "credit cards", "bank account numbers", "auth tokens",
            "security questions and answers", "government issued ids", "passport numbers",
            "social security numbers", "credit card cvv", "private messages"}
HIGH = {"partial credit card data", "phone numbers", "physical addresses", "dates of birth",
        "password hints", "historical passwords", "ip addresses", "geographic locations"}
MEDIUM = {"names", "usernames", "genders", "employers", "social media profiles"}

# 項目ごとの推奨対応（キー: action id）
ACTIONS = {
    "passwords": "change_password",
    "historical passwords": "change_password",
    "password hints": "change_password",
    "auth tokens": "change_password",
    "security questions and answers": "change_password",
    "credit cards": "contact_card_issuer",
    "credit card cvv": "contact_card_issuer",
    "partial credit card data": "watch_card_statement",
    "bank account numbers": "contact_bank",
    "phone numbers": "watch_smishing",
    "email addresses": "watch_phishing",
    "physical addresses": "watch_mail_fraud",
    "government issued ids": "contact_authority",
    "passport numbers": "contact_authority",
}

ACTION_TEXT = {
    "change_password": "漏洩元サービスと、同じパスワードを使い回しているサービスのパスワードを変更し、2段階認証を有効にする",
    "contact_card_issuer": "カード会社に連絡し、カードの停止・再発行を相談する（電話番号はカード裏面で確認）",
    "watch_card_statement": "カード明細に身に覚えのない請求がないか確認する",
    "contact_bank": "銀行に連絡し、不正出金がないか確認する",
    "watch_smishing": "SMSでの偽の不在通知・請求に注意する（リンクは開かない）",
    "watch_phishing": "このメールアドレス宛のフィッシングメールに注意する",
    "watch_mail_fraud": "郵送での架空請求などに注意する",
    "contact_authority": "身分証の発行元に相談する",
}


def classify(breach: Breach) -> str:
    items = {d.lower() for d in breach.data_classes}
    if items & CRITICAL:
        level = "critical"
    elif items & HIGH:
        level = "high"
    elif items & MEDIUM:
        level = "medium"
    else:
        level = "low"
    if not breach.is_verified and level != "low":
        level = LEVELS[LEVELS.index(level) - 1]
    return level


def recommended_actions(breach: Breach) -> list[str]:
    out = []
    for d in breach.data_classes:
        a = ACTIONS.get(d.lower())
        if a and a not in out:
            out.append(a)
    return out
