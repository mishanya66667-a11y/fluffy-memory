FROM debian:bullseye-slim

# Установка Asterisk и Python
RUN apt-get update && apt-get install -y \
    asterisk \
    python3 \
    python3-pip \
    sox \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Копирование конфигов
COPY asterisk/configs/pjsip.conf /etc/asterisk/
COPY asterisk/configs/extensions.conf /etc/asterisk/

# Копирование AGI скрипта
COPY agi/ /usr/local/agi/
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# Порты
EXPOSE 5060/udp 10000-10100/udp 4573

CMD ["asterisk", "-f", "-vvv"]
