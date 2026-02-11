# 🚀 AI Call Center - Шпаргалка

## Быстрый старт

```bash
# Полная автоматическая установка
sudo ./install.sh

# Автоматическая без вопросов
sudo ./install_auto.sh

# С кастомными настройками
sudo SERVER_IP=10.0.0.5 AI_PROVIDER=anthropic ANTHROPIC_API_KEY=sk-ant-xxx ./install_auto.sh
```

## Управление

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Перезапуск
docker compose restart

# Логи в реальном времени
docker compose logs -f

# Проверка статуса
docker compose ps

# Пересборка и запуск
docker compose up -d --build
```

## Диагностика

```bash
# Полная диагностика системы
sudo ./diagnose.sh

# Проверка Asterisk
docker exec ai-callcenter asterisk -r

# Внутри Asterisk консоли:
pjsip show endpoints    # SIP пользователи
pjsip show contacts     # Подключения
core show channels      # Активные звонки
agi show commands       # AGI команды
core show version       # Версия
```

## Логи

```bash
# Все логи
docker compose logs -f

# Только Asterisk
docker compose logs -f asterisk

# Последние 100 строк
docker compose logs --tail=100

# AGI логи
tail -f agi/logs/agi_*.log
```

## Конфигурация

```bash
# Показать SIP настройки
python3 show_microsip_config.py

# Посмотреть config.json
cat config.json | jq

# Посмотреть .env
cat .env
```

## Изменение настроек

```bash
# 1. Остановить контейнер
docker compose down

# 2. Изменить .env или config.json
nano .env

# 3. Перезапустить
docker compose up -d --build
```

## Ollama

```bash
# Проверка статуса
ollama --version
systemctl status ollama

# Список моделей
ollama list

# Загрузка новой модели
ollama pull llama3

# Тест модели
ollama run llama2 "Привет!"

# Удаление модели
ollama rm llama2
```

## Сеть

```bash
# Проверка портов
netstat -tuln | grep -E '5060|10000'

# Или через ss
ss -tuln | grep -E '5060|10000'

# Проверка IP
hostname -I

# Тест SIP порта
nc -zv 192.168.1.X 5060
```

## Firewall (если нужно)

```bash
# UFW
sudo ufw allow 5060/udp
sudo ufw allow 10000:10100/udp

# iptables
sudo iptables -A INPUT -p udp --dport 5060 -j ACCEPT
sudo iptables -A INPUT -p udp --dport 10000:10100 -j ACCEPT
sudo iptables-save
```

## Полная переустановка

```bash
# 1. Остановить и удалить контейнер
docker compose down -v

# 2. Удалить конфиги (если нужно)
rm .env config.json CREDENTIALS.txt

# 3. Переустановить
sudo ./install.sh
```

## Обновление

```bash
# Обновить код
git pull

# Пересобрать контейнер
docker compose down
docker compose up -d --build
```

## Бэкап

```bash
# Бэкап конфигов
tar -czf backup-$(date +%Y%m%d).tar.gz .env config.json agi/ recordings/

# Восстановление
tar -xzf backup-20250211.tar.gz
```

## Переменные окружения для install_auto.sh

```bash
# Базовые
PROJECT_NAME=ai-callcenter
SERVER_IP=192.168.1.100
SIP_PORT=5060
RTP_START=10000
RTP_END=10100

# SIP
SIP_USER=user1
SIP_PASSWORD=auto_generated
SIP_EXTENSION=100
SIP_DISPLAY_NAME=User1

# AI
AI_PROVIDER=ollama              # или: anthropic, openai, google
AI_MODEL=llama2
OLLAMA_URL=http://localhost:11434
AI_LANGUAGE=русский
AI_SYSTEM_PROMPT="Ваш промпт"

# API ключи
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Голос
TTS_PROVIDER=openai             # или: google, yandex
STT_PROVIDER=whisper            # или: google, yandex
ENABLE_RECORDING=false
```

## Тестовые звонки

После настройки SIP-клиента:

- **100** - эхо-тест (повторяет ваши слова)
- **101** - AI ассистент (разговор с AI)

## Проблемы и решения

### Docker не запускается

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Ollama не работает

```bash
sudo systemctl start ollama
sudo systemctl status ollama
ollama list
```

### Контейнер не стартует

```bash
# Проверить логи
docker compose logs

# Проверить конфиги
cat .env
cat docker-compose.yml
```

### SIP не регистрируется

```bash
# Проверить endpoints
docker exec ai-callcenter asterisk -rx "pjsip show endpoints"

# Проверить порты
netstat -tuln | grep 5060

# Проверить IP в config
cat config.json | grep server_ip
```

### AI не отвечает

```bash
# Проверить логи AGI
tail -f agi/logs/agi_*.log

# Проверить Ollama (если используется)
ollama list
ollama run llama2 "тест"

# Проверить API ключ (если облачный)
grep API_KEY .env
```

---

**Документация:**
- [README_LINUX.md](README_LINUX.md) - полная документация
- [README.md](README.md) - краткое описание

**Скрипты:**
- `install.sh` - автоустановка (интерактивная)
- `install_auto.sh` - автоустановка (без UI)
- `diagnose.sh` - диагностика системы
- `setup.py` - настройка проекта

**Управление:**
- `docker-compose.yml` - конфигурация Docker
- `.env` - переменные окружения
- `config.json` - конфигурация проекта
