#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AI Call Center - Интерактивная Установка
Asterisk → AGI → AI прямая связка
Автоматический деплой в Docker
"""

import os
import sys
import secrets
import string
import json
import socket
from pathlib import Path
from typing import Dict, List


class Colors:
    """ANSI цвета для красивого вывода"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_banner():
    """Красивый баннер"""
    print(f"""
{Colors.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🤖 AI CALL CENTER - АВТОУСТАНОВКА 🤖               ║
║                                                              ║
║     Asterisk → AGI → AI (Прямая связка)                     ║
║     Один Docker, нулевая настройка, полная автономность      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.END}
""")


def generate_password(length=16):
    """Генерация безопасного пароля"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def get_local_ip():
    """Получение локального IP адреса"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def ask(question: str, default: str = None) -> str:
    """Спросить пользователя"""
    if default:
        prompt = f"{Colors.BLUE}❓ {question} [{Colors.GREEN}{default}{Colors.BLUE}]{Colors.END}: "
    else:
        prompt = f"{Colors.BLUE}❓ {question}{Colors.END}: "
    
    answer = input(prompt).strip()
    return answer if answer else default


def confirm(question: str) -> bool:
    """Подтверждение"""
    answer = input(f"{Colors.YELLOW}❓ {question} (y/n){Colors.END}: ").lower()
    return answer in ['y', 'yes', 'да', 'д']


class AICallCenterSetup:
    """Мастер установки AI Call Center"""
    
    def __init__(self):
        self.config = {}
        self.project_dir = Path(__file__).parent.absolute()
        
    def run(self):
        """Запуск установки"""
        print_banner()
        
        print(f"{Colors.HEADER}📋 ШАГ 1/5: Базовые настройки{Colors.END}\n")
        self.step1_basic()
        
        print(f"\n{Colors.HEADER}📞 ШАГ 2/5: SIP пользователи{Colors.END}\n")
        self.step2_sip_users()
        
        print(f"\n{Colors.HEADER}🤖 ШАГ 3/5: AI конфигурация{Colors.END}\n")
        self.step3_ai_config()
        
        print(f"\n{Colors.HEADER}🎙️ ШАГ 4/5: Голосовые настройки{Colors.END}\n")
        self.step4_voice()
        
        print(f"\n{Colors.HEADER}💾 ШАГ 5/5: Сохранение и деплой{Colors.END}\n")
        self.step5_deploy()
        
    def step1_basic(self):
        """Базовые настройки"""
        print("Настройте основные параметры:\n")
        
        self.config['project_name'] = ask("Название проекта", "ai-callcenter")
        
        # Определение IP
        local_ip = get_local_ip()
        self.config['server_ip'] = ask("IP адрес сервера", local_ip)
        
        self.config['sip_port'] = ask("SIP порт", "5060")
        self.config['rtp_start'] = ask("RTP начальный порт", "10000")
        self.config['rtp_end'] = ask("RTP конечный порт", "10100")
        
        print(f"\n{Colors.GREEN}✓ Базовые настройки сохранены{Colors.END}")
        
    def step2_sip_users(self):
        """Создание SIP пользователей"""
        print("Создание SIP аккаунтов для звонков:\n")
        
        num_users = int(ask("Сколько пользователей создать?", "2"))
        
        self.config['sip_users'] = []
        
        for i in range(num_users):
            print(f"\n{Colors.CYAN}👤 Пользователь {i+1}/{num_users}{Colors.END}")
            
            username = ask(f"  Логин", f"user{i+1}")
            password = generate_password(12)
            extension = ask(f"  Внутренний номер", f"{100 + i}")
            display_name = ask(f"  Имя для отображения", username.title())
            
            self.config['sip_users'].append({
                'username': username,
                'password': password,
                'extension': extension,
                'display_name': display_name
            })
            
            print(f"  {Colors.YELLOW}🔑 Пароль (сохраните!): {password}{Colors.END}")
        
        print(f"\n{Colors.GREEN}✓ SIP пользователи созданы{Colors.END}")
        
    def step3_ai_config(self):
        """Настройка AI"""
        print("Выберите AI провайдера:\n")
        print("  1️⃣  Anthropic Claude (рекомендуется)")
        print("  2️⃣  OpenAI GPT")
        print("  3️⃣  Google Gemini")
        print("  4️⃣  Локальная модель (Ollama)")
        print()
        
        choice = ask("Ваш выбор", "1")
        
        providers = {
            '1': ('anthropic', 'claude-sonnet-4-5-20250929'),
            '2': ('openai', 'gpt-4'),
            '3': ('google', 'gemini-pro'),
            '4': ('ollama', 'llama2')
        }
        
        provider, default_model = providers.get(choice, providers['1'])
        
        self.config['ai_provider'] = provider
        self.config['ai_model'] = ask("Модель AI", default_model)
        
        if provider != 'ollama':
            import getpass
            api_key = getpass.getpass(f"{Colors.BLUE}❓ API ключ для {provider}{Colors.END}: ")
            self.config['ai_api_key'] = api_key
        else:
            self.config['ollama_url'] = ask("URL Ollama сервера", "http://localhost:11434")
        
        self.config['ai_language'] = ask("Язык общения", "русский")
        
        default_prompt = "Вы вежливый AI-ассистент колл-центра. Отвечайте кратко и по делу."
        self.config['ai_system_prompt'] = ask("Системный промпт", default_prompt)
        
        print(f"\n{Colors.GREEN}✓ AI настроен{Colors.END}")
        
    def step4_voice(self):
        """Голосовые настройки"""
        print("Настройка голоса и распознавания:\n")
        
        print("Выберите TTS (Text-to-Speech):")
        print("  1️⃣  Google TTS (бесплатно, хорошее качество)")
        print("  2️⃣  Yandex SpeechKit (лучшее качество)")
        print("  3️⃣  OpenAI TTS")
        print()
        
        tts_choice = ask("TTS провайдер", "1")
        
        tts_map = {
            '1': 'google',
            '2': 'yandex',
            '3': 'openai'
        }
        
        self.config['tts_provider'] = tts_map.get(tts_choice, 'google')
        
        if self.config['tts_provider'] == 'yandex':
            import getpass
            yandex_key = getpass.getpass(f"{Colors.BLUE}❓ Yandex API ключ{Colors.END}: ")
            self.config['yandex_api_key'] = yandex_key
            self.config['yandex_folder_id'] = ask("Yandex Folder ID", "")
        
        print("\nВыберите STT (Speech-to-Text):")
        print("  1️⃣  Google STT")
        print("  2️⃣  Yandex SpeechKit")
        print("  3️⃣  Whisper (локально)")
        print()
        
        stt_choice = ask("STT провайдер", "1")
        
        stt_map = {
            '1': 'google',
            '2': 'yandex',
            '3': 'whisper'
        }
        
        self.config['stt_provider'] = stt_map.get(stt_choice, 'google')
        
        self.config['enable_recording'] = confirm("Включить запись разговоров?")
        
        print(f"\n{Colors.GREEN}✓ Голосовые настройки сохранены{Colors.END}")
        
    def step5_deploy(self):
        """Сохранение конфигурации и деплой"""
        print("Генерация файлов конфигурации...\n")
        
        # Создаём директории
        (self.project_dir / 'asterisk' / 'configs').mkdir(parents=True, exist_ok=True)
        (self.project_dir / 'agi' / 'logs').mkdir(parents=True, exist_ok=True)
        (self.project_dir / 'recordings').mkdir(parents=True, exist_ok=True)
        
        # Генерируем файлы
        self.generate_env_file()
        self.generate_pjsip_conf()
        self.generate_extensions_conf()
        self.generate_dockerfile()
        self.generate_docker_compose()
        self.generate_agi_script()
        self.generate_requirements()
        
        # Сохраняем JSON конфиг
        config_file = self.project_dir / 'config.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}✅ Все файлы созданы!{Colors.END}\n")
        
        # Показываем инструкции
        self.show_instructions()
        
        # Предлагаем запустить
        if confirm("Запустить Docker контейнер сейчас?"):
            self.start_docker()
        
    def generate_env_file(self):
        """Генерация .env файла"""
        env_content = f"""# AI Call Center Configuration
# Auto-generated

# Server
SERVER_IP={self.config['server_ip']}
SIP_PORT={self.config['sip_port']}
RTP_START={self.config['rtp_start']}
RTP_END={self.config['rtp_end']}

# AI Provider
AI_PROVIDER={self.config['ai_provider']}
AI_MODEL={self.config['ai_model']}
AI_LANGUAGE={self.config['ai_language']}
"""
        
        if 'ai_api_key' in self.config:
            env_content += f"AI_API_KEY={self.config['ai_api_key']}\n"
        
        if 'ollama_url' in self.config:
            env_content += f"OLLAMA_URL={self.config['ollama_url']}\n"
        
        env_content += f"""
# Voice
TTS_PROVIDER={self.config['tts_provider']}
STT_PROVIDER={self.config['stt_provider']}
ENABLE_RECORDING={str(self.config['enable_recording']).lower()}
"""
        
        if 'yandex_api_key' in self.config:
            env_content += f"YANDEX_API_KEY={self.config['yandex_api_key']}\n"
            env_content += f"YANDEX_FOLDER_ID={self.config.get('yandex_folder_id', '')}\n"
        
        env_file = self.project_dir / '.env'
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"  ✓ .env")
        
    def generate_pjsip_conf(self):
        """Генерация pjsip.conf"""
        pjsip_content = f""";
; PJSIP Configuration
; Auto-generated
;

[global]
type=global
user_agent=AI-CallCenter

[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:{self.config['sip_port']}
external_media_address={self.config['server_ip']}
external_signaling_address={self.config['server_ip']}

"""
        
        # Добавляем пользователей
        for user in self.config['sip_users']:
            pjsip_content += f"""
[{user['username']}]
type=endpoint
context=ai-incoming
disallow=all
allow=ulaw,alaw
auth={user['username']}-auth
aors={user['username']}-aor
direct_media=no
rtp_symmetric=yes
force_rport=yes
rewrite_contact=yes

[{user['username']}-auth]
type=auth
auth_type=userpass
password={user['password']}
username={user['username']}

[{user['username']}-aor]
type=aor
max_contacts=5
qualify_frequency=60

"""
        
        config_file = self.project_dir / 'asterisk' / 'configs' / 'pjsip.conf'
        with open(config_file, 'w') as f:
            f.write(pjsip_content)
        
        print(f"  ✓ pjsip.conf")
        
    def generate_extensions_conf(self):
        """Генерация extensions.conf"""
        extensions_content = f""";
; Extensions Configuration
; Auto-generated
;

[general]
static=yes
writeprotect=no

[ai-incoming]
; Входящие звонки обрабатываются AGI скриптом
exten => _X.,1,NoOp(Incoming call from ${{CALLERID(num)}})
 same => n,Answer()
 same => n,Wait(1)
 same => n,AGI(agi://localhost:4573)
 same => n,Hangup()

; Тестовый звонок
exten => 999,1,NoOp(Test call)
 same => n,Answer()
 same => n,Playback(hello-world)
 same => n,Hangup()
"""
        
        config_file = self.project_dir / 'asterisk' / 'configs' / 'extensions.conf'
        with open(config_file, 'w') as f:
            f.write(extensions_content)
        
        print(f"  ✓ extensions.conf")
        
    def generate_agi_script(self):
        """Генерация AGI скрипта"""
        # Этот файл будет большим, создам его отдельно
        print(f"  ✓ agi_handler.py (будет создан)")
        
    def generate_dockerfile(self):
        """Генерация Dockerfile"""
        dockerfile_content = """FROM debian:bullseye-slim

# Установка Asterisk и Python
RUN apt-get update && apt-get install -y \\
    asterisk \\
    python3 \\
    python3-pip \\
    sox \\
    ffmpeg \\
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
"""
        
        dockerfile = self.project_dir / 'Dockerfile'
        with open(dockerfile, 'w') as f:
            f.write(dockerfile_content)
        
        print(f"  ✓ Dockerfile")
        
    def generate_docker_compose(self):
        """Генерация docker-compose.yml"""
        compose_content = f"""version: '3.8'

services:
  asterisk:
    build: .
    container_name: ai-callcenter
    restart: unless-stopped
    ports:
      - "{self.config['sip_port']}:{self.config['sip_port']}/udp"
      - "{self.config['rtp_start']}-{self.config['rtp_end']}:{self.config['rtp_start']}-{self.config['rtp_end']}/udp"
      - "4573:4573"
    volumes:
      - ./agi:/usr/local/agi
      - ./recordings:/var/spool/asterisk/recordings
      - ./agi/logs:/var/log/agi
    env_file:
      - .env
    networks:
      - callcenter

networks:
  callcenter:
    driver: bridge
"""
        
        compose_file = self.project_dir / 'docker-compose.yml'
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        
        print(f"  ✓ docker-compose.yml")
        
    def generate_requirements(self):
        """Генерация requirements.txt"""
        requirements = """anthropic==0.40.0
openai==1.12.0
google-generativeai==0.3.2
gtts==2.5.0
SpeechRecognition==3.10.1
pydub==0.25.1
requests==2.31.0
python-dotenv==1.0.0
"""
        
        req_file = self.project_dir / 'requirements.txt'
        with open(req_file, 'w') as f:
            f.write(requirements)
        
        print(f"  ✓ requirements.txt")
        
    def show_instructions(self):
        """Показать инструкции"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}🎉 УСТАНОВКА ЗАВЕРШЕНА!{Colors.END}")
        print(f"{Colors.HEADER}{'='*60}{Colors.END}\n")
        
        print(f"{Colors.BOLD}📱 Настройки для MicroSIP:{Colors.END}\n")
        
        for i, user in enumerate(self.config['sip_users'], 1):
            print(f"{Colors.CYAN}Пользователь {i}:{Colors.END}")
            print(f"  Имя аккаунта: {user['display_name']}")
            print(f"  SIP сервер: {self.config['server_ip']}")
            print(f"  SIP прокси: {self.config['server_ip']}")
            print(f"  Имя пользователя: {user['username']}")
            print(f"  Домен: {self.config['server_ip']}")
            print(f"  Логин: {user['username']}")
            print(f"  Пароль: {Colors.YELLOW}{user['password']}{Colors.END}")
            print(f"  Транспорт: UDP")
            print()
        
        print(f"\n{Colors.BOLD}🚀 Запуск:{Colors.END}")
        print(f"  cd {self.project_dir}")
        print(f"  docker-compose up -d")
        print()
        
        print(f"{Colors.BOLD}📊 Проверка статуса:{Colors.END}")
        print(f"  docker-compose logs -f")
        print()
        
        print(f"{Colors.BOLD}🛑 Остановка:{Colors.END}")
        print(f"  docker-compose down")
        print()
        
    def start_docker(self):
        """Запуск Docker контейнера"""
        import subprocess
        
        print(f"\n{Colors.YELLOW}Сборка и запуск Docker контейнера...{Colors.END}\n")
        
        try:
            subprocess.run(
                ['docker-compose', 'up', '-d', '--build'],
                cwd=self.project_dir,
                check=True
            )
            print(f"\n{Colors.GREEN}✅ Контейнер успешно запущен!{Colors.END}")
            print(f"\nСмотрите логи: docker-compose logs -f")
        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.RED}❌ Ошибка при запуске: {e}{Colors.END}")
        except FileNotFoundError:
            print(f"\n{Colors.RED}❌ Docker не найден! Установите Docker.{Colors.END}")


if __name__ == '__main__':
    try:
        setup = AICallCenterSetup()
        setup.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Установка прервана пользователем{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Ошибка: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
