import asyncio
import logging
import sys

from dotenv import load_dotenv

import config
from telethon import TelegramClient

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("login")


async def login_all():
    log.info("=== Первичная авторизация аккаунтов ===")

    for acc in config.ACCOUNTS:
        label, phone = acc["label"], acc["phone"]
        log.info(f"\n[{label}] Авторизация {phone}...")
        log.info(f"[{label}] Введи код, который придёт в Telegram для ЭТОГО аккаунта")

        client = TelegramClient(f"sessions/account_{label}", config.API_ID, config.API_HASH)
        try:
            await client.start(phone=phone)
            me = await client.get_me()
            log.info(f"[{label}] Успех! Вошёл как: {me.first_name} (@{me.username})")
            await client.disconnect()
        except Exception as e:
            log.error(f"[{label}] Ошибка: {e}")

    log.info("\n=== Все сессии сохранены в папке sessions/ ===")
    log.info("Теперь можно запускать основного бота: python main.py")


if __name__ == "__main__":
    asyncio.run(login_all())
