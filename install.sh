#!/bin/bash

# AI Call Center - Полностью автоматическая установка для Linux
# Устанавливает Docker, Ollama, зависимости и запускает проект

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Логирование
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Баннер
clear
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       🤖 AI CALL CENTER - АВТОМАТИЧЕСКАЯ УСТАНОВКА 🤖        ║
║                                                              ║
║     Asterisk → AGI → AI (Прямая связка)                     ║
║     Полная автоустановка: Docker + Ollama + Зависимости     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF

log_info "Начало установки..."
echo

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    log_error "Запустите скрипт с правами root: sudo ./install.sh"
    exit 1
fi

# Определение дистрибутива
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    log_error "Не удалось определить дистрибутив Linux"
    exit 1
fi

log_info "Обнаружен: $PRETTY_NAME"
echo

# ============================================================
# ШАГ 1: Установка базовых зависимостей
# ============================================================
log_info "ШАГ 1/6: Установка базовых пакетов..."

if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    apt-get update -qq
    apt-get install -y -qq \
        curl \
        wget \
        git \
        python3 \
        python3-pip \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        software-properties-common \
        net-tools \
        > /dev/null 2>&1
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
    yum install -y -q \
        curl \
        wget \
        git \
        python3 \
        python3-pip \
        ca-certificates \
        net-tools \
        > /dev/null 2>&1
else
    log_warning "Неподдерживаемый дистрибутив. Попробуйте установить вручную."
fi

log_success "Базовые пакеты установлены"
echo

# ============================================================
# ШАГ 2: Установка Docker
# ============================================================
log_info "ШАГ 2/6: Установка Docker..."

if command -v docker &> /dev/null; then
    log_warning "Docker уже установлен ($(docker --version))"
else
    log_info "Установка Docker Engine..."
    
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Удаление старых версий
        apt-get remove -y docker docker-engine docker.io containerd runc > /dev/null 2>&1 || true
        
        # Добавление репозитория Docker
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
          $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        apt-get update -qq
        apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin > /dev/null 2>&1
        
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
        yum install -y yum-utils
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    fi
    
    # Запуск Docker
    systemctl start docker
    systemctl enable docker > /dev/null 2>&1
    
    log_success "Docker установлен: $(docker --version)"
fi

# Проверка Docker Compose
if ! docker compose version &> /dev/null; then
    log_error "Docker Compose не установлен"
    exit 1
fi

log_success "Docker Compose: $(docker compose version --short)"
echo

# ============================================================
# ШАГ 3: Установка Ollama
# ============================================================
log_info "ШАГ 3/6: Установка Ollama..."

if command -v ollama &> /dev/null; then
    log_warning "Ollama уже установлен ($(ollama --version))"
else
    log_info "Загрузка и установка Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh > /dev/null 2>&1
    
    # Запуск Ollama как сервис
    systemctl start ollama > /dev/null 2>&1 || true
    systemctl enable ollama > /dev/null 2>&1 || true
    
    log_success "Ollama установлен: $(ollama --version)"
fi

# Загрузка модели llama2
log_info "Загрузка модели llama2 (это займёт несколько минут, ~3.8 GB)..."
if ollama list | grep -q "llama2"; then
    log_warning "Модель llama2 уже установлена"
else
    ollama pull llama2 > /dev/null 2>&1 &
    OLLAMA_PID=$!
    
    # Прогресс-бар
    while kill -0 $OLLAMA_PID 2>/dev/null; do
        echo -n "."
        sleep 2
    done
    echo
    
    wait $OLLAMA_PID
    log_success "Модель llama2 загружена"
fi
echo

# ============================================================
# ШАГ 4: Установка Python зависимостей
# ============================================================
log_info "ШАГ 4/6: Установка Python зависимостей..."

pip3 install --quiet --upgrade pip > /dev/null 2>&1

if [ -f "requirements.txt" ]; then
    pip3 install --quiet -r requirements.txt > /dev/null 2>&1
    log_success "Python зависимости установлены"
else
    log_warning "requirements.txt не найден, пропускаем"
fi
echo

# ============================================================
# ШАГ 5: Конфигурация проекта
# ============================================================
log_info "ШАГ 5/6: Настройка проекта..."

# Определение IP адреса
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="127.0.0.1"
fi

log_info "Обнаружен IP: $SERVER_IP"

# Запуск интерактивной настройки
if [ -f "config.json" ]; then
    log_warning "Конфигурация уже существует"
    read -p "Перенастроить проект? (y/n): " RECONFIG
    if [ "$RECONFIG" = "y" ]; then
        python3 setup.py
    fi
else
    log_info "Запуск интерактивной настройки..."
    python3 setup.py
fi

log_success "Проект настроен"
echo

# ============================================================
# ШАГ 6: Запуск контейнера
# ============================================================
log_info "ШАГ 6/6: Сборка и запуск Docker контейнера..."

# Остановка старого контейнера
docker compose down > /dev/null 2>&1 || true

# Сборка и запуск
log_info "Сборка образа (это может занять несколько минут)..."
docker compose build --quiet

log_info "Запуск контейнера..."
docker compose up -d

# Ожидание запуска
sleep 5

# Проверка статуса
if docker compose ps | grep -q "Up"; then
    log_success "Контейнер запущен!"
else
    log_error "Ошибка запуска контейнера"
    docker compose logs
    exit 1
fi

echo

# ============================================================
# ИТОГИ
# ============================================================
cat << "EOF"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                     ✅ УСТАНОВКА ЗАВЕРШЕНА!                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF

log_success "Все компоненты установлены и запущены:"
echo
echo "  ✓ Docker Engine"
echo "  ✓ Docker Compose"
echo "  ✓ Ollama + llama2"
echo "  ✓ AI Call Center контейнер"
echo

log_info "Настройки для SIP-клиента:"
if [ -f "config.json" ]; then
    python3 show_microsip_config.py 2>/dev/null || cat config.json
fi

echo
log_info "Управление контейнером:"
echo
echo "  📊 Просмотр логов:"
echo "     docker compose logs -f"
echo
echo "  🔄 Перезапуск:"
echo "     docker compose restart"
echo
echo "  🛑 Остановка:"
echo "     docker compose down"
echo
echo "  🚀 Запуск:"
echo "     docker compose up -d"
echo

log_info "Проверка работы Asterisk:"
echo "  docker exec ai-callcenter asterisk -rx 'pjsip show endpoints'"
echo

log_success "Готово! Настройте SIP-клиент и звоните! 🤖📞"
echo
