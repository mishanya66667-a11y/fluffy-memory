@echo off
chcp 65001 >nul
cls

echo ================================================================
echo   🔍 Проверка готовности AI Call Center
echo ================================================================
echo.

set ALL_OK=1

echo [1/4] Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo     ❌ Docker не установлен
    echo        Скачать: https://www.docker.com/products/docker-desktop
    set ALL_OK=0
) else (
    for /f "tokens=*" %%i in ('docker --version') do echo     ✅ %%i
)
echo.

echo [2/4] Проверка Docker Desktop (запущен ли)...
docker ps >nul 2>&1
if errorlevel 1 (
    echo     ❌ Docker Desktop не запущен
    echo        Запустите Docker Desktop и дождитесь его готовности
    set ALL_OK=0
) else (
    echo     ✅ Docker Desktop работает
)
echo.

echo [3/4] Проверка Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo     ❌ Ollama не установлен
    echo        Скачать: https://ollama.com/download
    set ALL_OK=0
) else (
    for /f "tokens=*" %%i in ('ollama --version') do echo     ✅ %%i
    
    echo     🔍 Проверка модели llama2...
    ollama list | findstr llama2 >nul 2>&1
    if errorlevel 1 (
        echo        ⚠️  Модель llama2 не установлена
        echo           Запустите: install_ollama_model.bat
        set ALL_OK=0
    ) else (
        echo        ✅ Модель llama2 готова
    )
)
echo.

echo [4/4] Проверка конфигурации проекта...
if exist "config.json" (
    echo     ✅ Конфигурация найдена
) else (
    echo     ❌ Конфигурация не найдена
    echo        Запустите: python setup.py
    set ALL_OK=0
)
echo.

echo ================================================================
if %ALL_OK%==1 (
    echo   ✅ ВСЁ ГОТОВО!
    echo ================================================================
    echo.
    echo 🚀 Запустить AI Call Center:
    echo    start.bat
) else (
    echo   ⚠️  ТРЕБУЮТСЯ ДОПОЛНИТЕЛЬНЫЕ ДЕЙСТВИЯ
    echo ================================================================
    echo.
    echo 📋 Выполните шаги с ❌ выше
)
echo.

pause
