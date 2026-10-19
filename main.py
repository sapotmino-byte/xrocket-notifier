import asyncio
import logging
import sys

from telethon import errors

import config
from listener import start_all_listeners, stop_all_listeners
from sender import sender
from server import start_health_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("xrocket_notifier.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

log = logging.getLogger("main")


async def main():
    log.info("=== xRocket Notifier запускается ===")

    if not config.API_ID or not config.API_HASH:
        log.error("API_ID / API_HASH не заданы в .env")
        return

    if not config.BOT_TOKEN:
        log.error("BOT_TOKEN не задан в .env")
        return

    if not config.ACCOUNTS:
        log.error("ACCOUNTS не заданы в .env")
        return

    await sender.start()

    if await start_health_server():
        log.info("HTTP health-сервер запущен (режим облачного хостинга)")

    listeners = await start_all_listeners()

    if not listeners:
        log.error("Ни один аккаунт не запустился. Выход.")
        await sender.stop()
        return

    log.info(f"Запущено аккаунтов: {len(listeners)}. Слушаю уведомления...")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        log.info("Остановка по Ctrl+C")
    finally:
        await stop_all_listeners(listeners)
        await sender.stop()
        log.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
    except errors.RPCError as e:
        log.error(f"RPC ошибка: {e}")
