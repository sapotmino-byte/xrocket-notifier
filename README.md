# xRocket Notifier

Telegram-бот, который ловит уведомления от @xrocket (платежи, сделки, выводы) с нескольких аккаунтов и пересылает их в твой канал с меткой аккаунта.

## Как это работает

1. Юзер-сессии (Telethon) мониторят чат с @xrocket
2. Фильтр отбирает только важные сообщения (платежи/сделки)
3. Бот-клиент пересылает их в твой канал с меткой аккаунта

## Установка

### 1. Получить API-ключи Telegram

1. Иди на https://my.telegram.org/apps
2. Войди под своим номером
3. Создай приложение (App title, App platform)
4. Скопируй **api_id** и **api_hash**

### 2. Создать бота через @BotFather

1. Открой @BotFather в Telegram
2. `/newbot` → задай имя и username
3. Скопируй **токен бота**

### 3. Создать канал для уведомлений

1. Создай **приватный** канал
2. Добавь своего бота как **админа** канала
3. Узнай **ID канала**:
   - Способ 1: перешли сообщение из канала боту @userinfobot
   - Способ 2: в клиенте Telegram Desktop ПКМ на канале → «Копировать ссылку» (там будет ID)

### 4. Настроить `.env`

```env
API_ID=12345678
API_HASH=your_api_hash
BOT_TOKEN=123456:ABC-token
NOTIFY_CHANNEL=-1001234567890
ACCOUNTS=Solov-1:+79991112233,Solov-2:+79994445566
XROCKET_USERNAME=xrocket
```

Формат `ACCOUNTS`: `метка:телефон,метка2:телефон2`

### 5. Установить зависимости

```bash
pip install -r requirements.txt
```

### 6. Запустить

```bash
python main.py
```

При первом запуске для каждого аккаунта Telethon попросит код из Telegram (введи код из СМС или из Telegram-приложения) и, если включена 2FA, пароль 2FA.

После этого сессии сохранятся в `sessions/` и повторный вход не нужен.

## Настройка фильтра

Ключевые слова — в `config.py` в списке `KEYWORDS`:

```python
KEYWORDS = [
    "получен", "отправлен", "вывод", "депозит",
    "чек", "счёт оплачен", "сделка", "p2p", ...
]
```

Если сообщения от @xrocket не проходят фильтр — добавь нужное слово в `KEYWORDS`. Исключения — в `SPAM_KEYWORDS`.

## Запуск на VPS (24/7)

### systemd (Linux)

Создай `/etc/systemd/system/xrocket-notifier.service`:

```ini
[Unit]
Description=xRocket Notifier
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/xrocket-notifier
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Потом:

```bash
sudo systemctl enable xrocket-notifier
sudo systemctl start xrocket-notifier
sudo journalctl -u xrocket-notifier -f
```

## Облачный запуск без ПК

### Вариант 1: Oracle Cloud (бесплатно навсегда, рекомендую)

1. Регистрация на https://www.oracle.com/cloud/free/ (нужна карта для верификации, не списывают)
2. Создай бесплатную VPS (A1 Flex ARM, до 24GB RAM на free tier)
3. Загрузи проект (scp/git), запусти `python main.py` внутри systemd-сервиса выше
4. Сессии лежат в `sessions/` на диске сервера — ничего дополнительно не нужно

### Вариант 2: Render.com (бесплатно, нужно 2 хака)

Render free уснет через 15 мин без HTTP — поэтому:

1. **Сессии в строках** (диск у Render временный):
   ```bash
   python export_sessions.py
   ```
   Скрипт допишет `SESSION_STRINGS=...` в `.env`
2. **HTTP-пинг**: в `.env` задай `PORT=8000`; на Render создай Web Service (Docker или Python), ставь Start Command `python main.py`
3. Добавь бесплатный пингер https://uptimerobot.com → монитор HTTP на URL приложения каждые 5 мин — бот не уснёт

## Тесты парсера

```bash
python test_parser.py
```

## Логи

Все логи пишутся в `xrocket_notifier.log`.

## ⚠️ Важно

- **Никогда не комить** файл `.env` и папку `sessions/` — это доступ к твоим Telegram-аккаунтам
- Юзер-сессии могут быть забанены Telegram при подозрительной активности — не злоупотребляй
- Сообщения от ботов не попадают в Bot API — поэтому нужен именно MTProto (Telethon) с юзер-аккаунтами
