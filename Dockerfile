FROM debian:bullseye-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    asterisk \
    python3 \
    python3-pip \
    python3-dev \
    sox \
    ffmpeg \
    libsox-fmt-all \
    build-essential \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip
RUN pip3 install --upgrade pip setuptools wheel

# Копируем requirements и устанавливаем Python зависимости
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Предзагрузка модели Faster-Whisper для ускорения первого запуска
RUN python3 -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"

# Копируем конфиги Asterisk
COPY asterisk/configs/pjsip.conf /etc/asterisk/
COPY asterisk/configs/extensions.conf /etc/asterisk/

# Копируем AGI скрипты
COPY agi/ /usr/local/agi/
RUN chmod +x /usr/local/agi/*.py

# Создаём директории для логов
RUN mkdir -p /var/log/agi /tmp/agi_speed

# Порты
EXPOSE 5060/udp 10000-10100/udp 4573

# Запуск
CMD ["asterisk", "-f", "-vvv"]
