import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    bot = TelegramClient("sessions/bot_session", API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    print(f"\nБот подключён: @{me.username}\n")
    print("=" * 50)
    print("Теперь напиши ЛЮБОЕ сообщение в своём канале")
    print("(можно просто поставить точку).")
    print("Скрипт покажет ID канала. Ctrl+C для выхода.")
    print("=" * 50 + "\n")

    @bot.on(events.NewMessage)
    async def handler(event):
        chat = event.chat
        if chat:
            print(f"ID: {chat.id}")
            print(f"Название: {getattr(chat, 'title', chat.id)}")
            print("-" * 30)

    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
