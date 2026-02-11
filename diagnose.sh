#!/bin/bash

# AI Call Center - Диагностика системы
# Проверяет все компоненты и показывает статус

set +e  # Не выходить при ошибках

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

clear
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🔍 AI CALL CENTER - ДИАГНОСТИКА СИСТЕМЫ 🔍          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF

ISSUES_FOUND=0

# ============================================================
# 1. DOCKER
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐳 DOCKER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    log_success "Docker установлен: $DOCKER_VERSION"
    
    if systemctl is-active --quiet docker; then
        log_success "Docker сервис запущен"
    else
        log_error "Docker сервис НЕ запущен"
        ISSUES_FOUND=$((ISSUES_FOUND+1))
    fi
    
    if docker ps &> /dev/null; then
        log_success "Docker работает корректно"
    else
        log_error "Docker не может запустить контейнеры"
        ISSUES_FOUND=$((ISSUES_FOUND+1))
    fi
else
    log_error "Docker НЕ установлен"
    ISSUES_FOUND=$((ISSUES_FOUND+1))
fi

echo

# ============================================================
# 2. DOCKER COMPOSE
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐙 DOCKER COMPOSE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version --short)
    log_success "Docker Compose установлен: $COMPOSE_VERSION"
else
    log_error "Docker Compose НЕ установлен"
    ISSUES_FOUND=$((ISSUES_FOUND+1))
fi

echo

# ============================================================
# 3. OLLAMA
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🦙 OLLAMA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "config.json" ]; then
    AI_PROVIDER=$(grep -Po '"ai_provider":\s*"\K[^"]*' config.json 2>/dev/null)
    
    if [ "$AI_PROVIDER" = "ollama" ]; then
        if command -v ollama &> /dev/null; then
            OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
            log_success "Ollama установлен: $OLLAMA_VERSION"
            
            if systemctl is-active --quiet ollama; then
                log_success "Ollama сервис запущен"
            else
                log_warning "Ollama сервис НЕ запущен (будет запущен автоматически)"
            fi
            
            # Проверка модели
            AI_MODEL=$(grep -Po '"ai_model":\s*"\K[^"]*' config.json 2>/dev/null)
            if ollama list | grep -q "$AI_MODEL"; then
                log_success "Модель $AI_MODEL установлена"
                
                # Тест модели
                log_info "Тест модели $AI_MODEL..."
                TEST_RESPONSE=$(ollama run $AI_MODEL "Скажи 'ок'" 2>&1 | head -n 1)
                if [ ! -z "$TEST_RESPONSE" ]; then
                    log_success "Модель отвечает: $TEST_RESPONSE"
                else
                    log_warning "Модель не отвечает (возможно перегружена)"
                fi
            else
                log_error "Модель $AI_MODEL НЕ установлена"
                echo "          Запустите: ollama pull $AI_MODEL"
                ISSUES_FOUND=$((ISSUES_FOUND+1))
            fi
        else
            log_error "Ollama НЕ установлен (требуется для AI_PROVIDER=ollama)"
            ISSUES_FOUND=$((ISSUES_FOUND+1))
        fi
    else
        log_info "AI провайдер: $AI_PROVIDER (Ollama не требуется)"
    fi
else
    log_warning "config.json не найден, пропускаем проверку Ollama"
fi

echo

# ============================================================
# 4. PYTHON
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐍 PYTHON"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log_success "Python установлен: $PYTHON_VERSION"
    
    if command -v pip3 &> /dev/null; then
        log_success "pip3 установлен"
        
        # Проверка зависимостей
        if [ -f "requirements.txt" ]; then
            log_info "Проверка Python зависимостей..."
            MISSING_DEPS=0
            while IFS= read -r package; do
                package_name=$(echo $package | sed 's/[>=<].*//' | tr -d '[:space:]')
                if [ ! -z "$package_name" ] && [ "${package_name:0:1}" != "#" ]; then
                    if ! pip3 show $package_name &> /dev/null; then
                        log_warning "Пакет $package_name НЕ установлен"
                        MISSING_DEPS=$((MISSING_DEPS+1))
                    fi
                fi
            done < requirements.txt
            
            if [ $MISSING_DEPS -eq 0 ]; then
                log_success "Все Python зависимости установлены"
            else
                log_warning "$MISSING_DEPS зависимостей НЕ установлены"
                echo "          Запустите: pip3 install -r requirements.txt"
            fi
        fi
    else
        log_error "pip3 НЕ установлен"
        ISSUES_FOUND=$((ISSUES_FOUND+1))
    fi
else
    log_error "Python3 НЕ установлен"
    ISSUES_FOUND=$((ISSUES_FOUND+1))
fi

echo

# ============================================================
# 5. КОНФИГУРАЦИЯ
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  КОНФИГУРАЦИЯ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".env" ]; then
    log_success ".env файл найден"
else
    log_error ".env файл НЕ найден"
    ISSUES_FOUND=$((ISSUES_FOUND+1))
fi

if [ -f "config.json" ]; then
    log_success "config.json найден"
    
    # Показываем основные настройки
    SERVER_IP=$(grep -Po '"server_ip":\s*"\K[^"]*' config.json 2>/dev/null)
    SIP_PORT=$(grep -Po '"sip_port":\s*"\K[^"]*' config.json 2>/dev/null)
    AI_PROVIDER=$(grep -Po '"ai_provider":\s*"\K[^"]*' config.json 2>/dev/null)
    AI_MODEL=$(grep -Po '"ai_model":\s*"\K[^"]*' config.json 2>/dev/null)
    
    echo "  ├─ Server IP: $SERVER_IP"
    echo "  ├─ SIP Port: $SIP_PORT"
    echo "  ├─ AI Provider: $AI_PROVIDER"
    echo "  └─ AI Model: $AI_MODEL"
else
    log_error "config.json НЕ найден"
    echo "          Запустите: python3 setup.py"
    ISSUES_FOUND=$((ISSUES_FOUND+1))
fi

if [ -f "docker-compose.yml" ]; then
    log_success "docker-compose.yml найден"
else
    log_error "docker-compose.yml НЕ найден"
    ISSUES_FOUND=$((ISSUES_FOUND+1))
fi

echo

# ============================================================
# 6. DOCKER КОНТЕЙНЕР
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 DOCKER КОНТЕЙНЕР"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker compose ps 2>/dev/null | grep -q "Up"; then
    log_success "Контейнер ai-callcenter ЗАПУЩЕН"
    
    # Показываем статус
    docker compose ps
    
    # Проверка портов
    echo
    log_info "Проверка портов..."
    
    if netstat -tuln 2>/dev/null | grep -q ":5060"; then
        log_success "SIP порт 5060 открыт"
    else
        log_warning "SIP порт 5060 НЕ открыт"
    fi
    
    if netstat -tuln 2>/dev/null | grep -q ":10000"; then
        log_success "RTP порты открыты"
    else
        log_warning "RTP порты НЕ открыты"
    fi
    
    # Проверка Asterisk
    echo
    log_info "Проверка Asterisk внутри контейнера..."
    if docker exec ai-callcenter asterisk -rx "core show version" &> /dev/null; then
        ASTERISK_VERSION=$(docker exec ai-callcenter asterisk -rx "core show version" 2>/dev/null | head -n 1)
        log_success "Asterisk работает: $ASTERISK_VERSION"
        
        # Проверка SIP endpoints
        ENDPOINTS_COUNT=$(docker exec ai-callcenter asterisk -rx "pjsip show endpoints" 2>/dev/null | grep -c "Endpoint:")
        if [ $ENDPOINTS_COUNT -gt 0 ]; then
            log_success "SIP endpoints настроены: $ENDPOINTS_COUNT"
        else
            log_warning "SIP endpoints НЕ найдены"
        fi
    else
        log_error "Asterisk НЕ отвечает внутри контейнера"
        ISSUES_FOUND=$((ISSUES_FOUND+1))
    fi
    
else
    log_warning "Контейнер ai-callcenter НЕ запущен"
    echo "          Запустите: docker compose up -d"
fi

echo

# ============================================================
# 7. СЕТЬ
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 СЕТЬ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Показываем IP адреса
log_info "Сетевые интерфейсы:"
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | while read ip; do
    echo "  ├─ $ip"
done

# Проверка доступности портов
if command -v nc &> /dev/null; then
    log_info "Проверка доступности SIP порта..."
    if nc -zv 127.0.0.1 5060 2>&1 | grep -q "succeeded"; then
        log_success "SIP порт 5060 доступен"
    else
        log_warning "SIP порт 5060 недоступен"
    fi
else
    log_info "netcat (nc) не установлен, пропускаем проверку портов"
fi

echo

# ============================================================
# ИТОГИ
# ============================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

if [ $ISSUES_FOUND -eq 0 ]; then
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    ✅ ВСЁ РАБОТАЕТ ОТЛИЧНО!                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF
    log_success "Все компоненты установлены и работают"
    echo
    log_info "Система готова к работе!"
    echo
    echo "📱 Настройте SIP-клиент с этими параметрами:"
    echo "   python3 show_microsip_config.py"
else
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              ⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ ($ISSUES_FOUND)          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF
    log_warning "Найдено проблем: $ISSUES_FOUND"
    echo
    log_info "Прочитайте сообщения выше и исправьте проблемы"
    echo
    log_info "Для полной переустановки запустите:"
    echo "   sudo ./install.sh"
fi

echo
