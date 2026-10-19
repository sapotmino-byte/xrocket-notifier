import asyncio
import sys

import qrcode

import config
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

LOGIN_TIMEOUT = 45


async def qr_login_account(label: str):
    client = TelegramClient(f"sessions/account_{label}", config.API_ID, config.API_HASH)
    await client.connect()

    attempts = 0
    while attempts < 5:
        attempts += 1
        qr_login = await client.qr_login()

        print(f"\n=== [{label}] Попытка {attempts} ===")
        print("Отсканируй QR-код с телефона, где залогинен этот аккаунт:")
        print("  Телефон -> Настройки -> Устройства -> Привязать устройство\n")

        q = qrcode.QRCode(border=1)
        q.add_data(qr_login.url)
        q.print_ascii(invert=True)
        print(f"({qr_login.url})\n")

        try:
            user = await qr_login.wait(timeout=LOGIN_TIMEOUT)
            print(f"\n[{label}] УСПЕХ! Вошёл как: {user.first_name} (@{user.username})")
            await client.disconnect()
            return True
        except SessionPasswordNeededError:
            pwd = input(f"[{label}] На аккаунте 2FA. Введи пароль: ")
            await client.sign_in(password=pwd)
            user = await client.get_me()
            print(f"\n[{label}] УСПЕХ! Вошёл как: {user.first_name} (@{user.username})")
            await client.disconnect()
            return True
        except asyncio.TimeoutError:
            print(f"[{label}] Время вышло, генерирую новый QR...")
        except Exception as e:
            print(f"[{label}] Ошибка: {e.__class__.__name__}. Новый QR...")
            await asyncio.sleep(2)

    await client.disconnect()
    print(f"\n[{label}] Не удалось войти за 5 попыток")
    return False


async def main():
    labels = sys.argv[1:] if len(sys.argv) > 1 else [a["label"] for a in config.ACCOUNTS]
    print("=== Вход по QR-коду ===")
    print(f"Аккаунты: {', '.join(labels)}\n")

    for label in labels:
        ok = await qr_login_account(label)
        if not ok:
            print(f"\n[{label}] Пропускаю (не удалось)", "\n")

    print("\nГотово. Дальше: python main.py")


if __name__ == "__main__":
    asyncio.run(main())
