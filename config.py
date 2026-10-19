import os

from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

NOTIFY_CHANNEL_RAW = os.getenv("NOTIFY_CHANNEL", "")
try:
    NOTIFY_CHANNEL = int(NOTIFY_CHANNEL_RAW)
except ValueError:
    NOTIFY_CHANNEL = NOTIFY_CHANNEL_RAW

XROCKET_USERNAME = os.getenv("XROCKET_USERNAME", "xrocket")

ACCOUNTS = []
for entry in os.getenv("ACCOUNTS", "").split(","):
    entry = entry.strip()
    if not entry or ":" not in entry:
        continue
    label, phone = entry.split(":", 1)
    ACCOUNTS.append({"label": label.strip(), "phone": phone.strip()})

SESSION_STRINGS = {}
for entry in os.getenv("SESSION_STRINGS", "").split(","):
    entry = entry.strip()
    if not entry or ":" not in entry:
        continue
    label, session_string = entry.split(":", 1)
    SESSION_STRINGS[label.strip()] = session_string.strip()

import re


def compile_patterns(keywords):
    patterns = []
    for kw in keywords:
        patterns.append(re.compile(r"(?i)" + re.escape(kw)))
    return patterns


# Откуда деньги пришли / отправлены
KEYWORDS = [
    " получен",
    "получено",
    "поступление",
    "пополнен",
    "зачислено",
    " отправлен",
    "отправлено",
    "вывод",
    "выведен",
    "перевод",
    "чек ",
    "чек активирован",
    "счёт оплачен",
    "счет оплачен",
    "оплачен",
    "инвойс",
    "invoice",
    "сделка",
    "trade",
    "обмен",
    "exchanged",
    "куплено",
    "продано",
    "bought",
    "sold",
    "p2p",
    "успешно завершена",
    "completed",
    "deposit",
    "withdraw",
]

COMPILED_KEYWORDS = compile_patterns(KEYWORDS)

# ПоРазделThese are "spam" keywords — messages with these are IGNORED even if they match above
SPAM_KEYWORDS = [
    "реклама",
    "новости",
    "news",
    "курс",
    "rate",
    "подписаться",
    "subscribe",
    "продлить",
]

COMPILED_SPAM = compile_patterns(SPAM_KEYWORDS)
