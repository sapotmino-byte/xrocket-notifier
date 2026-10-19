import logging

from telethon import TelegramClient

import config

log = logging.getLogger("sender")


class ChannelSender:
    def __init__(self):
        self.client = None

    async def start(self):
        self.client = TelegramClient(
            "sessions/bot_session",
            config.API_ID,
            config.API_HASH,
        )
        await self.client.start(bot_token=config.BOT_TOKEN)
        log.info("Bot client запущен")

    async def send_to_channel(self, label: str, text: str):
        if not self.client:
            log.error("Bot client не запущен")
            return

        message = f"🔔 [{label}]\n\n{text}"
        try:
            await self.client.send_message(
                config.NOTIFY_CHANNEL,
                message,
                parse_mode="html",
                link_preview=False,
            )
        except Exception as e:
            log.error(f"Ошибка отправки в канал: {e}")

    async def stop(self):
        if self.client:
            await self.client.disconnect()


sender = ChannelSender()
