#!/bin/bash
set -e

echo "==============================================="
echo "  AI Call Center - Starting Asterisk"
echo "==============================================="

# Установка прав доступа
chown -R asterisk:asterisk /var/log/asterisk
chown -R asterisk:asterisk /var/spool/asterisk
chown -R asterisk:asterisk /var/lib/asterisk
chown -R asterisk:asterisk /var/run/asterisk

# Проверка конфигурации
echo "Checking Asterisk configuration..."
asterisk -rx "core show version" 2>/dev/null || true

# Вывод конфигурации для отладки
echo ""
echo "SIP Configuration:"
echo "=================="
if [ -f /etc/asterisk/pjsip.conf ]; then
    echo "✓ pjsip.conf found"
    grep -E '^\[.*\]|^type=' /etc/asterisk/pjsip.conf | head -20
else
    echo "✗ pjsip.conf not found!"
fi

echo ""
echo "Extensions Configuration:"
echo "========================"
if [ -f /etc/asterisk/extensions.conf ]; then
    echo "✓ extensions.conf found"
    grep -E '^\[.*\]|^exten' /etc/asterisk/extensions.conf | head -20
else
    echo "✗ extensions.conf not found!"
fi

echo ""
echo "AGI Scripts:"
echo "============"
ls -la /usr/local/agi/ || echo "No AGI scripts found"

echo ""
echo "Environment Variables:"
echo "======================"
echo "AI_PROVIDER: ${AI_PROVIDER:-not set}"
echo "AI_MODEL: ${AI_MODEL:-not set}"
echo "TTS_PROVIDER: ${TTS_PROVIDER:-not set}"
echo "STT_PROVIDER: ${STT_PROVIDER:-not set}"

echo ""
echo "==============================================="
echo "  Starting Asterisk..."
echo "==============================================="
echo ""

# Запуск Asterisk
exec "$@"
