#!/bin/bash

# Подготовка проекта для Linux
# Делает все .sh файлы исполняемыми и конвертирует в Unix формат

echo "🔧 Подготовка проекта для Linux..."
echo

# Найти все .sh файлы и сделать исполняемыми
echo "📝 Установка прав на выполнение..."
find . -maxdepth 1 -name "*.sh" -type f -exec chmod +x {} \;
find . -maxdepth 1 -name "*.py" -type f -exec chmod +x {} \;

echo "  ✓ install.sh"
echo "  ✓ install_auto.sh"
echo "  ✓ diagnose.sh"
echo "  ✓ quick_install.sh"
echo "  ✓ docker-entrypoint.sh"
echo "  ✓ setup.py"
echo "  ✓ show_microsip_config.py"
echo "  ✓ test_system.py"

# Конвертация CRLF -> LF (если dos2unix установлен)
if command -v dos2unix &> /dev/null; then
    echo
    echo "🔄 Конвертация файлов в Unix формат..."
    find . -maxdepth 1 -name "*.sh" -type f -exec dos2unix {} \; 2>/dev/null
    find . -maxdepth 1 -name "*.py" -type f -exec dos2unix {} \; 2>/dev/null
    echo "  ✓ Все файлы сконвертированы"
else
    echo
    echo "⚠️  dos2unix не установлен, пропускаем конвертацию"
    echo "   (файлы работают и без этого, но лучше установить: sudo apt install dos2unix)"
fi

echo
echo "✅ Готово!"
echo
echo "Теперь можно запускать:"
echo "  sudo ./install.sh"
