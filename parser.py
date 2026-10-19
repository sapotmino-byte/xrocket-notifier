import re

DEAL_ID_RE = re.compile(r"\b(UD\d{3,15})\b", re.IGNORECASE)
AD_ID_RE = re.compile(r"\b(PA\d{3,15})\b", re.IGNORECASE)
CURRENCY_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*([A-Za-zА-ЯЁа-яё]{2,6})\b(?!\d)")
USDT_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*USDT", re.IGNORECASE)

NEW_TRADE_RE = re.compile(r"нов[а-яё]*\s+сделк", re.IGNORECASE)
BUY_RE = re.compile(r"покупк", re.IGNORECASE)
SALE_RE = re.compile(r"продаж", re.IGNORECASE)

BUYER_SENT = re.compile(r"покупател[ья]", re.IGNORECASE)
SENT_RE = re.compile(r"отправил", re.IGNORECASE)
SELLER_RE = re.compile(r"продавец", re.IGNORECASE)
CONFIRMED_RE = re.compile(r"подтвердил", re.IGNORECASE)


def to_plain(text: str) -> str:
    """Убирает HTML-теги, Markdown-разметку и схлопывает переносы строк."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_`~]+", "", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _find_fiat(plain: str):
    """Ищет последнюю сумму с валютой, где валюта не USDT."""
    fiat = None
    for m in CURRENCY_RE.finditer(plain):
        if m.group(2).upper() == "USDT":
            continue
        fiat = m.group(1), m.group(2).upper()
    return fiat


def _parse_new_trade(plain: str):
    deal = DEAL_ID_RE.search(plain)
    ad = AD_ID_RE.search(plain)
    usdt = USDT_RE.search(plain)
    fiat = _find_fiat(plain)

    missing = []
    if not deal:
        missing.append("ID сделки (UD...)")
    if not ad:
        missing.append("ID объявления (PA...)")
    if not usdt:
        missing.append("количество USDT")
    if not fiat:
        missing.append("сумма оплаты")
    if missing:
        return {"type": None, "error": "уведомление о новой сделке без данных: " + ", ".join(missing)}

    if BUY_RE.search(plain) and not SALE_RE.search(plain):
        etype = "new_trade_buy"
    elif SALE_RE.search(plain) and not BUY_RE.search(plain):
        etype = "new_trade_sale"
    else:
        return {"type": None, "error": "не удалось определить тип операции (покупка/продажа)"}

    return {
        "type": etype,
        "data": {
            "deal_id": deal.group(1).upper(),
            "ad_id": ad.group(1).upper(),
            "usdt": usdt.group(1),
            "fiat_amount": fiat[0],
            "fiat_currency": fiat[1],
        },
    }


def _parse_confirmation(plain: str):
    deal = DEAL_ID_RE.search(plain)
    usdt = USDT_RE.search(plain)
    fiat = _find_fiat(plain)

    missing = []
    if not deal:
        missing.append("ID сделки (UD...)")
    if not fiat:
        missing.append("сумма оплаты")
    if not usdt:
        missing.append("количество USDT")
    if missing:
        return {"type": None, "error": "уведомление о подтверждении оплаты без данных: " + ", ".join(missing)}

    return {
        "type": "payment_confirmed",
        "data": {
            "deal_id": deal.group(1).upper(),
            "usdt": usdt.group(1),
            "fiat_amount": fiat[0],
            "fiat_currency": fiat[1],
        },
    }


def _parse_buyer_payment(plain: str):
    deal = DEAL_ID_RE.search(plain)
    fiat = _find_fiat(plain)

    missing = []
    if not deal:
        missing.append("ID сделки (UD...)")
    if not fiat:
        missing.append("сумма перевода")
    if missing:
        return {"type": None, "error": "уведомление о платеже покупателя без данных: " + ", ".join(missing)}

    return {
        "type": "buyer_payment",
        "data": {
            "deal_id": deal.group(1).upper(),
            "fiat_amount": fiat[0],
            "fiat_currency": fiat[1],
        },
    }


def parse_notification(raw_text: str):
    """Определяет тип уведомления Rocket.

    Возвращает {"type": ..., "data": {...}} или {"type": None} /
    {"type": None, "error": причина}.
    """
    plain = to_plain(raw_text)
    if not plain:
        return {"type": None}

    if NEW_TRADE_RE.search(plain):
        return _parse_new_trade(plain)

    if BUYER_SENT.search(plain) and SENT_RE.search(plain):
        return _parse_buyer_payment(plain)

    if SELLER_RE.search(plain) and CONFIRMED_RE.search(plain):
        return _parse_confirmation(plain)

    return {"type": None}
