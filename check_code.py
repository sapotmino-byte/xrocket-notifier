import asyncio
import sys

import config
from telethon import TelegramClient, functions, types
from telethon.errors import (FloodWaitError, PhoneNumberBannedError,
                             PhoneNumberUnoccupiedError)


async def check(phone: str):
    client = TelegramClient("sessions/check", config.API_ID, config.API_HASH)
    await client.connect()

    try:
        result = await client(functions.auth.SendCodeRequest(
            phone_number=phone,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            settings=types.CodeSettings(),
        ))
        t = result.type
        name = type(t).__name__
        if "App" in name:
            print(f"[{phone}] Код отправлен В ПРИЛОЖЕНИЕ Telegram (в чат с 'Telegram')")
            print("   Смотри приложение Telegram этого аккаунта + push-уведомления!")
        elif "Sms" in name:
            print(f"[{phone}] Код отправлен ПО СМС на номер")
            print("   Смотри входящие СМС (может идти 2-5 минут)")
        elif "Call" in name or "Flash" in name:
            print(f"[{phone}] Код отправлен ЗВОНКОМ")
        else:
            print(f"[{phone}] Другой тип доставки: {name}")
        print(f"   Ожидание: {getattr(t, 'timeout', '?')} сек до повторной отправки")
    except PhoneNumberUnoccupiedError:
        print(f"[{phone}] НЕ ЗАРЕГИСТРИРОВАН в Telegram! Этого номера нет.")
    except PhoneNumberBannedError:
        print(f"[{phone}] Номер ЗАБАНЕН Telegram")
    except FloodWaitError as e:
        print(f"[{phone}] Слишком много запросов. Подожди {e.seconds} сек и попробуй снова")
    except Exception as e:
        print(f"[{phone}] Ошибка: {e.__class__.__name__}: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    phone = sys.argv[1] if len(sys.argv) > 1 else config.ACCOUNTS[0]["phone"]
    asyncio.run(check(phone))
