#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор конфигурации для MicroSIP
Читает config.json и создаёт готовые настройки для копирования в MicroSIP
"""

import json
import sys
from pathlib import Path


def load_config():
    """Загрузка конфигурации"""
    config_file = Path(__file__).parent / 'config.json'
    
    if not config_file.exists():
        print("❌ Файл config.json не найден!")
        print("Сначала запустите: python3 setup.py")
        sys.exit(1)
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_microsip_config(config):
    """Вывод конфигурации для MicroSIP"""
    print("\n" + "="*60)
    print("📱 НАСТРОЙКИ ДЛЯ MicroSIP")
    print("="*60 + "\n")
    
    server_ip = config['server_ip']
    sip_port = config.get('sip_port', '5060')
    
    for i, user in enumerate(config['sip_users'], 1):
        print(f"{'─'*60}")
        print(f"Пользователь {i}: {user['display_name']}")
        print(f"{'─'*60}")
        print(f"")
        print(f"  Название аккаунта:  {user['display_name']}")
        print(f"  ")
        print(f"  SIP сервер:         {server_ip}")
        print(f"  SIP прокси:         {server_ip}")
        print(f"  ")
        print(f"  Имя пользователя:   {user['username']}")
        print(f"  Домен:              {server_ip}")
        print(f"  Логин:              {user['username']}")
        print(f"  Пароль:             {user['password']}")
        print(f"  ")
        print(f"  Отображаемое имя:   {user['display_name']}")
        print(f"  ")
        print(f"  Транспорт:          UDP")
        print(f"  Публичный адрес:    Авто")
        print(f"  ")
        print(f"  ✓ Публиковать статус")
        print(f"  ✓ Использовать внешний IP-адрес")
        print(f"")
    
    print("="*60)
    print("\n💡 ИНСТРУКЦИЯ:")
    print("1. Откройте MicroSIP")
    print("2. Меню → Аккаунты → Добавить")
    print("3. Скопируйте данные из таблицы выше")
    print("4. Сохраните → Готово!")
    print("\n🎯 Для проверки позвоните на номер 999 (тестовый)")
    print("")


def generate_sip_uri(config):
    """Генерация SIP URI для быстрого добавления"""
    print("\n📋 БЫСТРАЯ РЕГИСТРАЦИЯ (SIP URI):\n")
    
    for user in config['sip_users']:
        uri = f"sip:{user['username']}:{user['password']}@{config['server_ip']}"
        print(f"  {user['display_name']}: {uri}")
    
    print("")


def main():
    """Главная функция"""
    try:
        config = load_config()
        print_microsip_config(config)
        generate_sip_uri(config)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
