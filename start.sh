#!/bin/bash

clear

echo "================================================================"
echo "  🤖 AI Call Center - Быстрый Старт"
echo "================================================================"
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден!"
    echo "📥 Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✓ Docker найден"
echo ""

# Проверка config.json
if [ ! -f "config.json" ]; then
    echo "📋 Конфигурация не найдена. Запуск настройки..."
    echo ""
    python3 setup.py
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Ошибка настройки"
        exit 1
    fi
fi

echo ""
echo "🚀 Запуск контейнера..."
echo ""

docker-compose up -d --build

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Ошибка запуска Docker"
    echo ""
    echo "💡 Попробуйте:"
    echo "   1. sudo systemctl start docker"
    echo "   2. docker-compose logs"
    echo ""
    exit 1
fi

echo ""
echo "✅ Контейнер запущен!"
echo ""
echo "📊 Проверка статуса..."
sleep 3

docker ps | grep ai-callcenter
echo ""

echo "================================================================"
echo "  🎉 Готово!"
echo "================================================================"
echo ""
echo "📱 Настройки для MicroSIP:"
echo "   python3 show_microsip_config.py"
echo ""
echo "📊 Просмотр логов:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Остановка:"
echo "   docker-compose down"
echo ""
echo "================================================================"
echo ""
