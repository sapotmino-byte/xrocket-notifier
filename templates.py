import html
from decimal import ROUND_HALF_UP, Decimal

DIV = "━━━━━━━━━━━━━━━━━━"


def _code(value: str) -> str:
    return f"<code>{html.escape(value)}</code>"


def _deal_code(deal_id: str) -> str:
    return _code(f"#{deal_id}")


def fmt_fiat(amount: str, currency: str) -> str:
    try:
        d = Decimal(str(amount).replace(",", "."))
        d = d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        value = f"{d:f}"
    except Exception:
        value = html.escape(str(amount))
    return _code(f"{value} {html.escape(str(currency))}")


def fmt_usdt(amount: str) -> str:
    value = str(amount).replace(",", ".")
    return _code(f"{html.escape(value)} USDT")


def build(etype: str, d: dict) -> str:
    deal = _deal_code(d["deal_id"])

    if etype == "new_trade_buy":
        return (
            "💸 <b>НОВАЯ СДЕЛКА</b>\n\n"
            f"{DIV}\n\n"
            f"🆔 <b>Сделка:</b> {deal}\n"
            f"📢 <b>Объявление:</b> {_deal_code(d['ad_id'])}\n\n"
            f"💰 <b>Получение:</b> {fmt_usdt(d['usdt'])}\n"
            f"💵 <b>Сумма:</b> {fmt_fiat(d['fiat_amount'], d['fiat_currency'])}\n"
            "🔄 <b>Операция:</b> Покупка\n\n"
            f"{DIV}\n\n"
            "⚡️ Rocket • Уведомление о сделке"
        )

    if etype == "new_trade_sale":
        return (
            "💸 <b>НОВАЯ СДЕЛКА • ПРОДАЖА USDT</b>\n\n"
            f"{DIV}\n\n"
            f"🆔 <b>Сделка:</b> {deal}\n\n"
            f"📢 <b>Объявление:</b> {_deal_code(d['ad_id'])}\n\n"
            f"💰 <b>Сумма USDT:</b> {fmt_usdt(d['usdt'])}\n\n"
            f"💵 <b>Сумма сделки:</b> {fmt_fiat(d['fiat_amount'], d['fiat_currency'])}\n\n"
            f"{DIV}\n\n"
            "⚡️ Rocket • Продажа USDT"
        )

    if etype == "payment_confirmed":
        return (
            "✅ <b>СДЕЛКА ЗАВЕРШЕНА</b>\n\n"
            f"{DIV}\n\n"
            f"🆔 <b>Сделка:</b> {deal}\n\n"
            f"💵 <b>Подтверждённая оплата:</b> {fmt_fiat(d['fiat_amount'], d['fiat_currency'])}\n"
            f"💰 <b>Куплено:</b> {fmt_usdt(d['usdt'])}\n\n"
            f"{DIV}\n\n"
            "⚡️ Rocket • Сделка подтверждена"
        )

    if etype == "buyer_payment":
        return (
            "💰 <b>ПОЛУЧЕН ПЛАТЁЖ ОТ ПОКУПАТЕЛЯ</b>\n\n"
            f"{DIV}\n\n"
            f"🆔 <b>Сделка:</b> {deal}\n\n"
            f"💵 <b>Покупатель отправил:</b> {fmt_fiat(d['fiat_amount'], d['fiat_currency'])}\n\n"
            "📌 <b>Статус:</b> Платёж отправлен\n\n"
            f"{DIV}\n\n"
            "⚡️ Rocket • Платёж по продаже USDT"
        )

    raise ValueError(f"неизвестный тип события: {etype}")
