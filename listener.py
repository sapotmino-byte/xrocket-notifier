
import html
import logging

from telethon import TelegramClient, events
from telethon.sessions import StringSession

import config
from filters import is_important, get_clean_text
from parser import parse_notification
from sender import sender
from storage import mark_seen, was_seen
from templates import build

log = logging.getLogger("listener")


class AccountListener:
    def __init__(self, label: str, phone: str, index: int):
        self.label = label
        self.phone = phone
        self.session_name = f"sessions/account_{label}"

        session_string = config.SESSION_STRINGS.get(label)

        if session_string:
            self.client = TelegramClient(
                StringSession(session_string),
                config.API_ID,
                config.API_HASH,
            )
            self.from_session_string = True
        else:
            self.client = TelegramClient(
                self.session_name,
                config.API_ID,
                config.API_HASH,
            )
            self.from_session_string = False

    async def start(self):
        if self.from_session_string:
            await self.client.connect()

            if not await self.client.is_user_authorized():
                raise RuntimeError(
                    f"Строка сессии для [{self.label}] не активна. "
                    "Проверь локальную авторизацию и обнови SESSION_STRINGS."
                )
        else:
            await self.client.start(phone=self.phone)

        me = await self.client.get_me()
        nick = config.ACCOUNT_NICKS.get(self.label, self.label)

        log.info(
            f"[{nick}] Вошёл как: {me.first_name} (@{me.username}) "
            f"phone={self.phone}"
        )

        target = await self.client.get_entity(config.XROCKET_USERNAME)

        @self.client.on(events.NewMessage(chats=target))
        async def handler(event):
            await self.on_xrocket_message(event)

        log.info(f"[{nick}] Слушаю @{config.XROCKET_USERNAME}")

    async def on_xrocket_message(self, event):
        raw = event.message.message or ""

        if not raw:
            return

        result = parse_notification(raw)
        etype = result.get("type")

        if etype:
            data = result["data"]
            key = f"{etype}:{data['deal_id']}"

            if was_seen(key):
                log.info(
                    f"[{self.label}] Дубликат {etype} "
                    f"#{data['deal_id']} — пропускаю"
                )
                return

            formatted = build(etype, data)
            mark_seen(key)

            log.info(
                f"[{self.label}] {etype} сделка "
                f"#{data['deal_id']} → отправляю по шаблону"
            )

            await sender.send_to_channel(self.label, formatted)
            return

        if result.get("error"):
            log.warning(f"[{self.label}] {result['error']}")
            return

        clean = get_clean_text(raw)

        if not is_important(clean):
            return

        log.info(
            f"[{self.label}] Уведомление без шаблона: {clean[:80]}..."
        )

        await sender.send_to_channel(self.label, html.escape(clean))

    async def stop(self):
        if self.client:
            await self.client.disconnect()


async def start_all_listeners() -> list:
    listeners = []

    for i, acc in enumerate(config.ACCOUNTS, 1):
        listener = AccountListener(acc["label"], acc["phone"], i)

        try:
            await listener.start()
            listeners.append(listener)
        except Exception as e:
            log.error(f"[{acc['label']}] Не удалось запустить: {e}")

    return listeners


async def stop_all_listeners(listeners):
    for listener in listeners:
        await listener.stop()
