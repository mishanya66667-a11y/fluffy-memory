# 🤖 AI Call Center - Полностью Автоматизированный

**Asterisk → AGI → AI** прямая связка без веб-сервера!

Звони и общайся с AI через обычный телефон или софтфон. **Полная автоматическая установка** всех зависимостей.

## ✨ Главные фишки

- ✅ **Полная автоустановка** - Docker, Ollama, зависимости устанавливаются автоматически
- ✅ **Два режима** - интерактивный (с вопросами) и автоматический (без UI)
- ✅ **Один скрипт** - всё в одном: `sudo ./install.sh`
- ✅ **Нулевая настройка** - работает из коробки
- ✅ **Безопасность** - случайные пароли, изоляция Docker
- ✅ **Множество AI** - Claude, GPT, Gemini, Ollama
- ✅ **Голос** - Google/Yandex/OpenAI TTS/STT
- ✅ **Кросс-платформенность** - Linux (основная), Windows (dev)

---

## 📚 Документация

- **[README_LINUX.md](README_LINUX.md)** - полная документация для Linux (основная)
- **[CHEATSHEET.md](CHEATSHEET.md)** - шпаргалка с командами
- **README.md** (этот файл) - краткое описание

---

## 🚀 Быстрый старт (Linux)

### Вариант 1: Интерактивная установка (рекомендуется)

```bash
git clone https://github.com/YOUR_REPO/ai-callcenter-direct.git
cd ai-callcenter-direct
sudo chmod +x install.sh
sudo ./install.sh
```

Скрипт **автоматически**:
1. Установит Docker и Docker Compose
2. Установит Ollama и загрузит модель llama2
3. Установит Python зависимости
4. Запустит интерактивную настройку
5. Соберёт и запустит контейнер

⏱️ **Время установки:** 5-10 минут

### Вариант 2: Автоматическая без вопросов

```bash
sudo chmod +x install_auto.sh
sudo ./install_auto.sh
```

Или с кастомными настройками:

```bash
sudo SERVER_IP=10.0.0.5 \
     AI_PROVIDER=anthropic \
     ANTHROPIC_API_KEY=sk-ant-xxx \
     ./install_auto.sh
```

### Вариант 3: Однострочная установка

```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/ai-callcenter-direct/main/install.sh | sudo bash
```

⚠️ **Проверяйте скрипты перед запуском с `sudo`!**

---

## 🪟 Windows (для разработки)

На Windows проект можно настроить через `setup.py`, но для запуска нужен Docker Desktop:

```powershell
# 1. Установить Docker Desktop
# 2. Установить Python
python setup.py
docker-compose up -d --build
```

**Рекомендуется:** использовать Linux для production.

---

## 📦 Что устанавливается автоматически

| Компонент | Описание | Linux | Windows |
|-----------|----------|-------|---------|
| **Docker Engine** | Контейнеризация | ✅ Авто | ⚠️ Вручную |
| **Docker Compose** | Оркестрация | ✅ Авто | ⚠️ Вручную |
| **Ollama** | Локальные LLM | ✅ Авто | ⚠️ Вручную |
| **llama2** | AI модель (3.8GB) | ✅ Авто | ⚠️ Вручную |
| **Python deps** | Зависимости | ✅ Авто | ✅ Авто |
| **Asterisk** | VoIP сервер | ✅ Docker | ✅ Docker |

---

## 🎯 Архитектура

```
┌─────────────┐
│  SIP Client │ (MicroSIP, Zoiper, Linphone)
└──────┬──────┘
       │ SIP call → 192.168.1.X:5060
       ↓
┌─────────────────────────────────────────────────┐
│  Docker: ai-callcenter                          │
│                                                 │
│  ┌────────────┐                                 │
│  │  Asterisk  │ ← принимает SIP вызов           │
│  └──────┬─────┘                                 │
│         │ AGI protocol (stdin/stdout)           │
│         ↓                                       │
│  ┌────────────────┐                             │
│  │ agi_handler.py │ ← Python AGI скрипт         │
│  ├────────────────┤                             │
│  │ TTS → Приветст │                             │
│  │ STT → Слушает  │                             │
│  │ AI  → Думает   │ ← Ollama/Claude/GPT         │
│  │ TTS → Отвечает │                             │
│  │ Loop → Повтор  │                             │
│  └────────────────┘                             │
└─────────────────────────────────────────────────┘
         │
         ↓
   ┌────────────┐
   │   Ollama   │ на хосте: localhost:11434
   │   llama2   │
   └────────────┘
```

---

## 🔧 Управление

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Логи
docker compose logs -f

# Диагностика
sudo ./diagnose.sh

# SIP настройки
python3 show_microsip_config.py
```

Полный список команд: **[CHEATSHEET.md](CHEATSHEET.md)**

---

## 🛠️ Системные требования

### Минимальные (Ollama)
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB
- OS: Ubuntu 20.04+, Debian 11+, CentOS 8+

### Для облачных AI (Claude/GPT)
- CPU: 2 cores
- RAM: 2 GB
- Disk: 5 GB
- Интернет + API ключ

---

## 📱 Настройка SIP-клиента

После установки получите настройки:

```bash
python3 show_microsip_config.py
```

Пример настроек:
```
SIP Server:    192.168.1.100
SIP Port:      5060
Login:         user1
Password:      [auto-generated]
Extension:     100
Transport:     UDP
```

### Рекомендуемые SIP-клиенты:

- **Linux:** Linphone, Zoiper
- **Windows:** MicroSIP, Zoiper
- **macOS:** Telephone, Zoiper
- **Android:** Linphone, Zoiper
- **iOS:** Linphone, Zoiper

---

## 🔍 Диагностика

```bash
# Полная диагностика
sudo ./diagnose.sh

# Проверка компонентов:
# ✓ Docker
# ✓ Docker Compose
# ✓ Ollama + модель
# ✓ Python + зависимости
# ✓ Конфигурация
# ✓ Docker контейнер
# ✓ Asterisk
# ✓ Сеть
```

---

## 📂 Структура проекта

```
ai-callcenter-direct/
│
├── 🚀 Установка
│   ├── install.sh              # Автоустановка (интерактивная)
│   ├── install_auto.sh         # Автоустановка (без UI)
│   ├── prepare_for_linux.sh    # Подготовка файлов для Linux
│   └── setup.py                # Настройка (вызывается из install.sh)
│
├── 🐳 Docker
│   ├── docker-compose.yml      # Docker оркестрация
│   ├── Dockerfile              # Образ контейнера
│   └── docker-entrypoint.sh    # Точка входа
│
├── ⚙️ Конфигурация
│   ├── .env                    # Переменные окружения (генерируется)
│   ├── config.json             # Конфигурация (генерируется)
│   └── CREDENTIALS.txt         # Учётные данные (генерируется)
│
├── 🤖 AGI
│   ├── agi/
│   │   ├── agi_handler.py      # Главный AGI скрипт
│   │   └── logs/               # Логи AGI
│   └── requirements.txt        # Python зависимости
│
├── 📞 Asterisk
│   └── asterisk/configs/
│       ├── pjsip.conf          # SIP конфигурация (генерируется)
│       └── extensions.conf     # Диалплан (генерируется)
│
├── 🔧 Утилиты
│   ├── diagnose.sh             # Диагностика системы
│   ├── show_microsip_config.py # Показать SIP настройки
│   ├── test_system.py          # Тесты
│   ├── start.bat               # Запуск (Windows)
│   └── start.sh                # Запуск (Linux)
│
├── 📖 Документация
│   ├── README.md               # Этот файл
│   ├── README_LINUX.md         # Полная документация (Linux)
│   └── CHEATSHEET.md           # Шпаргалка
│
└── 🎙️ Данные
    └── recordings/             # Записи звонков (если включено)
```

---

## 🐛 Проблемы и решения

### Docker не найден

```bash
sudo ./install.sh  # Установит автоматически
```

### Ollama не работает

```bash
sudo systemctl start ollama
ollama list
```

### Контейнер не запускается

```bash
docker compose logs
sudo ./diagnose.sh
```

### SIP не регистрируется

```bash
# Проверить настройки
cat config.json

# Проверить Asterisk
docker exec ai-callcenter asterisk -rx "pjsip show endpoints"
```

Полный список решений: **[README_LINUX.md](README_LINUX.md)**

---

## 🔐 Безопасность

### Автоматически:
- ✅ Случайные пароли для SIP
- ✅ Изоляция Docker
- ✅ Минимальные права
- ✅ Нет лишних открытых портов

### Рекомендуется:
- 🔒 Файрвол (ufw, iptables)
- 🔒 Изменить дефолтные порты
- 🔒 Не хранить API ключи в репозитории
- 🔒 Регулярно обновлять Docker образы

---

## 🎉 Готово!

**Звони и общайся с AI!** 🤖📞

Настройте SIP-клиент и начните разговаривать с AI через обычный телефон!

---

## 📞 Поддержка

- **Issues:** [GitHub Issues](https://github.com/YOUR_REPO/ai-callcenter-direct/issues)
- **Документация:** [README_LINUX.md](README_LINUX.md)
- **Шпаргалка:** [CHEATSHEET.md](CHEATSHEET.md)

---

## 📄 Лицензия

MIT License

---


