#!/usr/bin/env bash
# Автоустановка xRocket Notifier на сервер (Ubuntu 22/24, ARM в т.ч.)
# Запуск: bash oracle_setup.sh

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE="xrocket-notifier"

echo "=== xRocket Notifier: установка на сервер ==="
echo "Папка проекта: $PROJECT_DIR"

# 1. Python и venv
echo "--- Устанавливаю python3/venv (нужно sudo) ---"
sudo apt-get update -y -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip >/dev/null

# 2. Виртуальное окружение и зависимости
echo "--- Создаю venv и ставлю зависимости ---"
cd "$PROJECT_DIR"
python3 -m venv venv
./venv/bin/pip install --quiet --upgrade pip
./venv/bin/pip install --quiet -r requirements.txt

# 3. systemd-сервис
echo "--- Создаю systemd-сервис ---"
sudo tee /etc/systemd/system/${SERVICE}.service >/dev/null <<EOF
[Unit]
Description=xRocket Notifier (@xrocket -> канал)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE} >/dev/null 2>&1

echo ""
echo "=== Установка завершена! ==="
echo "Перед запуском останови бота на своём ПК (см. Шаг 6 в ORACLE.md)"
echo "Запуск:           sudo systemctl start ${SERVICE}"
echo "Проверка статуса: sudo systemctl status ${SERVICE}"
echo "Лог в реальном времени: sudo journalctl -u ${SERVICE} -f"
