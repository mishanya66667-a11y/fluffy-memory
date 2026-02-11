#!/bin/bash
# AI Call Center - ОДИН СКРИПТ ДЛЯ ВСЕГО
# Просто запусти: sudo ./install.sh

set -e
clear

echo "╔════════════════════════════════════════╗"
echo "║   🚀 AI CALL CENTER - АВТОЗАПУСК 🚀   ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Проверка root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Нужен root. Запусти: sudo ./install.sh"
    exit 1
fi

echo "⚡ Устанавливаю всё что нужно..."

# Установка базовых пакетов
apt-get update -qq > /dev/null 2>&1
apt-get install -y -qq python3 python3-pip sox ffmpeg curl git > /dev/null 2>&1

# Docker
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh > /dev/null 2>&1
    systemctl start docker
    systemctl enable docker > /dev/null 2>&1
fi

# Python пакеты
pip3 install -q --upgrade pip > /dev/null 2>&1
pip3 install -q groq faster-whisper gtts pydub soundfile requests python-dotenv > /dev/null 2>&1

echo "✅ Установка завершена"
echo ""
echo "⚡ Загружаю модель Whisper..."

# Предзагрузка модели
python3 -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')" 2>&1 | grep -v "Warning" || true

echo "✅ Модель готова"
echo ""
echo "⚡ Запускаю Docker..."

# Остановка старого контейнера
docker compose down > /dev/null 2>&1 || true

# Сборка и запуск
docker compose build -q
docker compose up -d

sleep 3

# Проверка запуска
if docker compose ps | grep -q "Up"; then
    echo "✅ Контейнер запущен!"
else
    echo "❌ Ошибка запуска"
    docker compose logs
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║         ✅ ВСЁ ГОТОВО! ✅             ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Получение IP
SERVER_IP=$(grep SERVER_IP .env | cut -d'=' -f2)
SIP_PASS=$(python3 -c "import json; print(json.load(open('config.json'))['sip_users'][0]['password'])")

echo "📱 НАСТРОЙ SIP КЛИЕНТ:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Сервер:  $SERVER_IP:5060"
echo "  Логин:   user1"
echo "  Пароль:  $SIP_PASS"
echo "  Номер:   100"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 ЗВОНИ НА НОМЕР 100 И ГОВОРИ С AI!"
echo ""
echo "📊 Логи: docker compose logs -f"
echo ""
