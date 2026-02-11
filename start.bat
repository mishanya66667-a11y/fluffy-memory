@echo off
chcp 65001 >nul
cls

echo ================================================================
echo   🤖 AI Call Center - Быстрый Старт
echo ================================================================
echo.

REM Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не найден!
    echo 📥 Установите Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✓ Docker найден
echo.

REM Проверка config.json
if not exist "config.json" (
    echo 📋 Конфигурация не найдена. Запуск настройки...
    echo.
    python setup.py
    if errorlevel 1 (
        echo.
        echo ❌ Ошибка настройки
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Запуск контейнера...
echo.

docker-compose up -d --build

if errorlevel 1 (
    echo.
    echo ❌ Ошибка запуска Docker
    echo.
    echo 💡 Попробуйте:
    echo    1. Перезапустить Docker Desktop
    echo    2. Проверить логи: docker-compose logs
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Контейнер запущен!
echo.
echo 📊 Проверка статуса...
timeout /t 3 /nobreak >nul

docker ps | findstr ai-callcenter
echo.

echo ================================================================
echo   🎉 Готово!
echo ================================================================
echo.
echo 📱 Настройки для MicroSIP:
echo    python show_microsip_config.py
echo.
echo 📊 Просмотр логов:
echo    docker-compose logs -f
echo.
echo 🛑 Остановка:
echo    docker-compose down
echo.
echo ================================================================
echo.

pause
