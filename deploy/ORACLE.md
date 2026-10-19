# Деплой xRocket Notifier на Oracle Cloud (Free Tier)

Полный путь от регистрации до работающего бота 24/7.

---

## Шаг 1. Регистрация в Oracle Cloud

1. Иди на https://www.oracle.com/cloud/free/
2. Нажми **Start for free** и заполни форму:
   - Email, имя (латиницей)
   - **Адрес**: реальный (где карта), страна — какая есть
   - **Банковская карта** — только для верификации; заморозят ~1$, вернут
   - Номер телефона — для СМС-кода
3. Выбирай **Home Region** ближе к тебе (например, Frankfurt/Zurich для СНГ точку входа; годится любой)
4. Подтверди email → вход в консоль

⚠️ Регистрация иногда не проходит с первого раза: попробуй другую карту / другой регион / инкогнито-браузер.

---

## Шаг 2. Создание бесплатного VPS

1. В консоли: Меню (☰) → **Compute → Instances → Create instance**
2. Настройки:
   - **Name**: `xrocket-notifier`
   - **Image**: `Ubuntu 24.04` (или 22.04)
   - **Shape**: **Ampere A1 Flex (ARM)** → OCPUs: `2`, Memory: `12 GB`
     (в free tier доступно до 4 OCPU / 24 GB; если пишет *Out of capacity* — ниже раздел «Если нет мощности»)
   - **SSH keys**: выбери **Generate a key pair**
     → скачай **Оба ключа**: приватный `.key` и публичный `.pub`
     ⚠️ Ключ `.key` скачивается один раз, не потеряй
   - Boot volume: 50 GB (хватает)
3. **Create** — жди, пока статус станет **RUNNING** (2-3 мин)
4. Запиши **Public IP address** из карточки инстанса

### Если нет мощности (Out of capacity)

Free-машины бывают заняты. Попробуй:
- Сменить **Availability Domain** (в зоне создания) и пересоздать
- Взять shape **VM.Standard.E2.1.Micro** (AMD, 1GB) — их free даёт 2 шт.
- Повторить через несколько часов — capacity появляется волнами

---

## Шаг 3. Подключение по SSH (с Windows)

Открой **cmd** на своём ПК:

```bash
ssh -i "C:\Users\DragonPC\Downloads\ssh-key-*.key" ubuntu@ПУБЛИЧНЫЙ_IP
```

(замени путь к скачанному ключу и IP)

При первом входе: `yes` → попадаешь в терминал Ubuntu сервера.

---

## Шаг 4. Загрузка проекта с ПК на сервер

В **cmd Windows** (не на сервере):

```bash
scp -i "C:\Users\DragonPC\Downloads\ssh-key-*.key" -r "C:\Users\DragonPC\Documents\Default Project\xrocket-notifier" ubuntu@ПУБЛИЧНЫЙ_IP:~/xrocket-notifier
```

Загрузится папка целиком, включая `.env` и готовые `sessions/` — **перелогин не нужен**.

---

## Шаг 5. Автоустановка на сервере

В терминале **сервера**:

```bash
cd ~/xrocket-notifier/deploy
bash oracle_setup.sh
```

Скрипт сам:
- установит python + venv
- поставит зависимости
- создаст systemd-сервис `xrocket-notifier`
- включит автозапуск при перезагрузке

---

## Шаг 6. ВАЖНО: останови бота на своём ПК

Перед стартом сервера **заверши локальную копию** (Ctrl+C в её консоли).
Один и тот же набор сессий, запущенный в двух местах одновременно, вызывает конфликты и логауты Telegram.

---

## Шаг 7. Запуск бота на сервере

```bash
sudo systemctl start xrocket-notifier
```

Проверка:

```bash
sudo systemctl status xrocket-notifier        # должно быть active (running)
sudo journalctl -u xrocket-notifier -f        # живой лог (Ctrl+C чтобы выйти)
```

В логе ищи: `[Акк-1] Слушаю @xrocket` × 3 аккаунта + `Запущено аккаунтов: 3`.

Готово — бот работает 24/7 без твоего ПК, переживает перезагрузки (автозапуск в systemd).

---

## Полезные команды сервера

| Действие | Команда |
|----------|---------|
| Старт | `sudo systemctl start xrocket-notifier` |
| Стоп | `sudo systemctl stop xrocket-notifier` |
| Рестарт | `sudo systemctl restart xrocket-notifier` |
| Лог в реальном времени | `sudo journalctl -u xrocket-notifier -f` |
| Лог файл (если есть) | внутри: `~/xrocket-notifier/xrocket_notifier.log` |

## Правки кода/настроек на сервере

После изменения любых файлов (например `.env`):

```bash
sudo systemctl restart xrocket-notifier
```

### Обновить проект с ПК (перезалить файлы)

Из cmd Windows (перезаписывает только изменённые файлы):

```bash
scp -i "путь\к\ключу.key" -r "C:\Users\DragonPC\Documents\Default Project\xrocket-notifier\*" ubuntu@ПУБЛИЧНЫЙ_IP:~/xrocket-notifier/ 2>nul & scp -i "путь\к\ключу.key" .env ubuntu@ПУБЛИЧНЫЙ_IP:~/xrocket-notifier/.env
```

Проще: заново выполнить команду Шага 4, подтвердив замену.

---

## Если что-то не работает

| Симптом | Причина/Решение |
|---------|-----------------|
| Сервис inactive, в логе `Строка сессии ... не активна` | В `.env` появился SESSION_STRINGS — очисти его (должен быть пустым) |
| `Сессий нет` / аккаунты не стартуют | В папке `sessions/` не попали файлы — перезаливай папку целиком |
| Конфликты, логаут уведомлений с обеих сторон | Локальный бот не остановлен (Шаг 6) |
| Решил вернуть бота на ПК | `sudo systemctl stop xrocket-notifier` и то же самое наоборот |

## Удаление (если вдруг)

```bash
sudo systemctl stop xrocket-notifier
sudo systemctl disable xrocket-notifier
sudo rm /etc/systemd/system/xrocket-notifier.service
sudo systemctl daemon-reload
```

Инстанс в консоли Oracle: **Terminate** — можно за 5 минут и вернуться позже.
