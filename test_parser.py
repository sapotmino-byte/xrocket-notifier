import sys

from parser import parse_notification
from storage import mark_seen, was_seen
from templates import build

BUY_1 = "💸 У Вас **новая сделка #UD1957542** в объявлении **#PA158006** на **покупку** **5.777007 USDT** за **500.0 RUB**."
BUY_2 = "💸 У Вас новая сделка #UD1234567 в объявлении #PA7654321 на покупку 1 USDT за 12345.5 USD."
SALE_1 = "💸 У Вас новая сделка #UD1957777 в объявлении #PA159993 на продажу 9.660869 USDT за 847.0 RUB."
SALE_2 = "💸 У Вас **новая сделка #UD99887766** в объявлении **#PA11223344**\n на **продажу** **1000 USDT** за **45.75 USD**."
CONF_1 = "💸 Продавец из сделки **#UD1957542** **подтвердил** получение от Вас **500.0 RUB**.\n\nВы купили: **5.777007 USDT**"
CONF_2 = "💸 Продавец из сделки **#UD99998888** **подтвердил** получение от Вас **12000 UAH**.\n\nВы купили: **2300,5 USDT**"
PAY_1 = "💸 Покупатель из сделки #UD1957777 отправил Вам 847.0 RUB"
PAY_2 = "💸 Покупатель из сделки **#UD55556666** отправил Вам **999.99 EUR**"
OTHER_1 = "🔥 Курс BTC вырос на 5% за последние 24 часа! Покупай выгодно."
INCOMPLETE = "💸 У Вас **новая сделка #UD11112222** в объявлении **#PA33334444**"
UNKNOWN_NU = "💸 У Вас новая сделка на непонятную операцию #UD22223333 10 USDT за 5 USD"

RUB = "RUB"
cases = [
    ("buy1", BUY_1, "new_trade_buy"),
    ("buy2-другие-ID/сумма/валюта", BUY_2, "new_trade_buy"),
    ("sale1", SALE_1, "new_trade_sale"),
    ("sale2-markdown+переносы", SALE_2, "new_trade_sale"),
    ("conf1", CONF_1, "payment_confirmed"),
    ("conf2-другая валюта", CONF_2, "payment_confirmed"),
    ("pay1", PAY_1, "buyer_payment"),
    ("pay2-другая валюта", PAY_2, "buyer_payment"),
    ("other-постороннее", OTHER_1, None),
    ("incomplete-нет сумм", INCOMPLETE, None),
    ("unknown-operation", UNKNOWN_NU, None),
]

all_ok = True
seen_keys = set()

for name, msg, expected in cases:
    res = parse_notification(msg)
    got = res.get("type")
    status = "OK " if got == expected else "FAIL"
    if got != expected:
        all_ok = False
    print(f"[{status}] {name}: type={got} (ожидался {expected})")
    if res.get("error"):
        print(f"        причина: {res['error']}")
    if got:
        key = f"{got}:{res['data']['deal_id']}"
        dup = key in seen_keys
        if not dup:
            seen_keys.add(key)
            out = build(got, res["data"])
            print("        " + out.replace("\n", "\n        "))
        print(f"        дубликат: {'ДА → не отправлять' if dup else 'нет'}")

print()
print("Итог:", "ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if all_ok else "ЕСТЬ ОШИБКИ")
sys.exit(0 if all_ok else 1)
