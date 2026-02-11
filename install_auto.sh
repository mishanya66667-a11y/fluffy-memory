#!/bin/bash

# AI Call Center - Полностью автоматическая установка БЕЗ ВОПРОСОВ
# Для CI/CD и автоматического деплоя

set -e

# ============================================================
# НАСТРОЙКИ (можно изменить перед запуском)
# ============================================================

# Базовые настройки
PROJECT_NAME="${PROJECT_NAME:-ai-callcenter}"
SERVER_IP="${SERVER_IP:-$(hostname -I | awk '{print $1}')}"
SIP_PORT="${SIP_PORT:-5060}"
RTP_START="${RTP_START:-10000}"
RTP_END="${RTP_END:-10100}"

# SIP пользователи (можно добавить больше через переменные)
SIP_USER="${SIP_USER:-user1}"
SIP_EXTENSION="${SIP_EXTENSION:-100}"
SIP_PASSWORD="${SIP_PASSWORD:-$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 12)}"
SIP_DISPLAY_NAME="${SIP_DISPLAY_NAME:-User1}"

# AI настройки
AI_PROVIDER="${AI_PROVIDER:-ollama}"
AI_MODEL="${AI_MODEL:-llama2}"
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
AI_LANGUAGE="${AI_LANGUAGE:-русский}"
AI_SYSTEM_PROMPT="${AI_SYSTEM_PROMPT:-Вы вежливый AI-ассистент колл-центра. Отвечайте кратко и по делу.}"

# Для других провайдеров (если нужно)
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"
GOOGLE_API_KEY="${GOOGLE_API_KEY:-}"

# Голосовые настройки
TTS_PROVIDER="${TTS_PROVIDER:-openai}"
STT_PROVIDER="${STT_PROVIDER:-whisper}"
ENABLE_RECORDING="${ENABLE_RECORDING:-false}"

# ============================================================
# ФУНКЦИИ
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# ============================================================
# НАЧАЛО УСТАНОВКИ
# ============================================================

clear
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🤖 AI CALL CENTER - АВТОМАТИЧЕСКАЯ УСТАНОВКА БЕЗ UI 🤖   ║
║                                                              ║
║     Полностью автоматическая установка без вопросов          ║
║     Для CI/CD, серверов, автоматического деплоя             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF

log_info "Режим: АВТОМАТИЧЕСКАЯ УСТАНОВКА"
log_info "IP: $SERVER_IP | Порт: $SIP_PORT"
log_info "AI: $AI_PROVIDER ($AI_MODEL)"
echo

# Проверка прав
if [ "$EUID" -ne 0 ]; then 
    log_error "Требуются права root: sudo ./install_auto.sh"
fi

# ============================================================
# УСТАНОВКА ЗАВИСИМОСТЕЙ
# ============================================================

log_info "Установка базовых пакетов..."
apt-get update -qq > /dev/null 2>&1
apt-get install -y -qq curl wget git python3 python3-pip apt-transport-https ca-certificates gnupg lsb-release software-properties-common net-tools > /dev/null 2>&1
log_success "Базовые пакеты установлены"

# ============================================================
# DOCKER
# ============================================================

log_info "Установка Docker..."
if ! command -v docker &> /dev/null; then
    apt-get remove -y docker docker-engine docker.io containerd runc > /dev/null 2>&1 || true
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    apt-get update -qq > /dev/null 2>&1
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin > /dev/null 2>&1
    
    systemctl start docker
    systemctl enable docker > /dev/null 2>&1
    
    log_success "Docker установлен"
else
    log_warning "Docker уже установлен"
fi

# ============================================================
# OLLAMA
# ============================================================

if [ "$AI_PROVIDER" = "ollama" ]; then
    log_info "Установка Ollama..."
    
    if ! command -v ollama &> /dev/null; then
        curl -fsSL https://ollama.com/install.sh | sh > /dev/null 2>&1
        systemctl start ollama > /dev/null 2>&1 || true
        systemctl enable ollama > /dev/null 2>&1 || true
        log_success "Ollama установлен"
    else
        log_warning "Ollama уже установлен"
    fi
    
    log_info "Загрузка модели $AI_MODEL..."
    if ! ollama list | grep -q "$AI_MODEL"; then
        ollama pull $AI_MODEL > /dev/null 2>&1
        log_success "Модель $AI_MODEL загружена"
    else
        log_warning "Модель $AI_MODEL уже установлена"
    fi
fi

# ============================================================
# PYTHON ЗАВИСИМОСТИ
# ============================================================

log_info "Установка Python зависимостей..."
pip3 install --quiet --upgrade pip > /dev/null 2>&1
if [ -f "requirements.txt" ]; then
    pip3 install --quiet -r requirements.txt > /dev/null 2>&1
    log_success "Python зависимости установлены"
fi

# ============================================================
# ГЕНЕРАЦИЯ КОНФИГУРАЦИИ
# ============================================================

log_info "Генерация конфигурационных файлов..."

# Создание .env
cat > .env << EOL
# AI Call Center Configuration
# Auto-generated by install_auto.sh

# Server
SERVER_IP=$SERVER_IP
SIP_PORT=$SIP_PORT
RTP_START=$RTP_START
RTP_END=$RTP_END

# AI Provider
AI_PROVIDER=$AI_PROVIDER
AI_MODEL=$AI_MODEL
AI_LANGUAGE=$AI_LANGUAGE
OLLAMA_URL=$OLLAMA_URL

# API Keys (if needed)
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
OPENAI_API_KEY=$OPENAI_API_KEY
GOOGLE_API_KEY=$GOOGLE_API_KEY

# Voice
TTS_PROVIDER=$TTS_PROVIDER
STT_PROVIDER=$STT_PROVIDER
ENABLE_RECORDING=$ENABLE_RECORDING
EOL

# Создание config.json
cat > config.json << EOL
{
  "project_name": "$PROJECT_NAME",
  "server_ip": "$SERVER_IP",
  "sip_port": "$SIP_PORT",
  "rtp_start": "$RTP_START",
  "rtp_end": "$RTP_END",
  "sip_users": [
    {
      "username": "$SIP_USER",
      "password": "$SIP_PASSWORD",
      "extension": "$SIP_EXTENSION",
      "display_name": "$SIP_DISPLAY_NAME"
    }
  ],
  "ai_provider": "$AI_PROVIDER",
  "ai_model": "$AI_MODEL",
  "ollama_url": "$OLLAMA_URL",
  "ai_language": "$AI_LANGUAGE",
  "ai_system_prompt": "$AI_SYSTEM_PROMPT",
  "tts_provider": "$TTS_PROVIDER",
  "stt_provider": "$STT_PROVIDER",
  "enable_recording": $ENABLE_RECORDING
}
EOL

log_success "Конфигурация создана"

# ============================================================
# ЗАПУСК DOCKER
# ============================================================

log_info "Сборка и запуск контейнера..."

docker compose down > /dev/null 2>&1 || true
docker compose build --quiet
docker compose up -d

sleep 5

if docker compose ps | grep -q "Up"; then
    log_success "Контейнер запущен!"
else
    log_error "Ошибка запуска контейнера"
fi

# ============================================================
# ИТОГИ
# ============================================================

echo
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                   ✅ УСТАНОВКА ЗАВЕРШЕНА!                    ║
╚══════════════════════════════════════════════════════════════╝

EOF

log_success "AI Call Center установлен и запущен!"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 НАСТРОЙКИ SIP КЛИЕНТА:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "  SIP Сервер:    $SERVER_IP"
echo "  SIP Порт:      $SIP_PORT"
echo "  Логин:         $SIP_USER"
echo "  Пароль:        $SIP_PASSWORD"
echo "  Номер:         $SIP_EXTENSION"
echo "  Имя:           $SIP_DISPLAY_NAME"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎛️ УПРАВЛЕНИЕ:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "  📊 Логи:       docker compose logs -f"
echo "  🔄 Перезапуск: docker compose restart"
echo "  🛑 Остановка:  docker compose down"
echo "  🚀 Запуск:     docker compose up -d"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Сохранение креденшалов
cat > CREDENTIALS.txt << EOL
AI CALL CENTER - Учётные данные
Сгенерированы: $(date)

SIP Сервер: $SERVER_IP:$SIP_PORT
Пользователь: $SIP_USER
Пароль: $SIP_PASSWORD
Номер: $SIP_EXTENSION

СОХРАНИТЕ ЭТОТ ФАЙЛ В БЕЗОПАСНОМ МЕСТЕ!
EOL

log_success "Учётные данные сохранены в: CREDENTIALS.txt"
log_success "Настройте SIP-клиент и звоните! 🤖📞"
echo
