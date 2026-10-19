import asyncio
import sys

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()

import config


async def export():
    strings = {}
    for acc in config.ACCOUNTS:
        label = acc["label"]
        path = f"sessions/account_{label}.session"
        try:
            client = TelegramClient(path.replace(".session", ""), config.API_ID, config.API_HASH)
            await client.connect()
            if not await client.is_user_authorized():
                print(f"[{label}] Сессия {path} не активна — пропустил", file=sys.stderr)
                await client.disconnect()
                continue
            s = StringSession.save(client.session)
            strings[label] = s
            await client.disconnect()
            print(f"[{label}] OK", file=sys.stderr)
        except FileNotFoundError:
            print(f"[{label}] Нет файла {path} — сначала войди через login.py или qr_login.py", file=sys.stderr)

    if not strings:
        print("Нет ни одной активной сессии для экспорта", file=sys.stderr)
        sys.exit(1)

    pairs = ",".join(f"{k}:{v}" for k, v in strings.items())
    print()
    print()

    try:
        with open(".env", encoding="utf-8") as f:
            env = f.read()
    except FileNotFoundError:
        env = ""

    if "SESSION_STRINGS=" in env:
        import re
        env = re.sub(r"SESSION_STRINGS=.*", f"SESSION_STRINGS={pairs}", env)
    else:
        env = env.rstrip() + f"\n\n# Строковые сессии для облачного запуска\nSESSION_STRINGS={pairs}\n"
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env)
    print(f"Экспортировано {len(strings)} сессий в .env (SESSION_STRINGS)", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(export())
