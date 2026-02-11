#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование AI Call Center системы
Проверка всех компонентов
"""

import subprocess
import sys
import time
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def run_command(cmd, check_output=False):
    """Выполнение команды"""
    try:
        if check_output:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0, result.stdout
        else:
            result = subprocess.run(cmd, shell=True, timeout=10)
            return result.returncode == 0, ""
    except Exception as e:
        return False, str(e)


def test_docker():
    """Проверка Docker"""
    print(f"{Colors.BLUE}🐳 Проверка Docker...{Colors.END}")
    
    success, output = run_command("docker --version", check_output=True)
    if success:
        print(f"  {Colors.GREEN}✓ Docker работает{Colors.END}")
        return True
    else:
        print(f"  {Colors.RED}✗ Docker не найден{Colors.END}")
        return False


def test_container():
    """Проверка контейнера"""
    print(f"\n{Colors.BLUE}📦 Проверка контейнера...{Colors.END}")
    
    success, output = run_command(
        "docker ps --filter name=ai-callcenter --format '{{.Status}}'",
        check_output=True
    )
    
    if success and "Up" in output:
        print(f"  {Colors.GREEN}✓ Контейнер запущен{Colors.END}")
        return True
    else:
        print(f"  {Colors.RED}✗ Контейнер не работает{Colors.END}")
        print(f"  {Colors.YELLOW}💡 Запустите: docker-compose up -d{Colors.END}")
        return False


def test_asterisk():
    """Проверка Asterisk"""
    print(f"\n{Colors.BLUE}☎️  Проверка Asterisk...{Colors.END}")
    
    success, output = run_command(
        'docker exec ai-callcenter asterisk -rx "core show version"',
        check_output=True
    )
    
    if success and "Asterisk" in output:
        print(f"  {Colors.GREEN}✓ Asterisk работает{Colors.END}")
        
        # Проверка SIP
        success, endpoints = run_command(
            'docker exec ai-callcenter asterisk -rx "pjsip show endpoints"',
            check_output=True
        )
        
        if success:
            endpoint_count = endpoints.count("Endpoint:")
            print(f"  {Colors.GREEN}✓ SIP эндпоинтов: {endpoint_count}{Colors.END}")
        
        return True
    else:
        print(f"  {Colors.RED}✗ Asterisk не отвечает{Colors.END}")
        return False


def test_agi_script():
    """Проверка AGI скрипта"""
    print(f"\n{Colors.BLUE}🤖 Проверка AGI скрипта...{Colors.END}")
    
    success, output = run_command(
        'docker exec ai-callcenter ls -la /usr/local/agi/agi_handler.py',
        check_output=True
    )
    
    if success and "agi_handler.py" in output:
        print(f"  {Colors.GREEN}✓ AGI скрипт найден{Colors.END}")
        
        # Проверка прав
        if "-rwx" in output or "x" in output:
            print(f"  {Colors.GREEN}✓ Права выполнения установлены{Colors.END}")
        else:
            print(f"  {Colors.YELLOW}⚠ Нет прав на выполнение{Colors.END}")
        
        return True
    else:
        print(f"  {Colors.RED}✗ AGI скрипт не найден{Colors.END}")
        return False


def test_python_deps():
    """Проверка Python зависимостей"""
    print(f"\n{Colors.BLUE}🐍 Проверка Python зависимостей...{Colors.END}")
    
    deps_to_check = [
        ('anthropic', 'Anthropic'),
        ('openai', 'OpenAI'),
        ('gtts', 'gTTS'),
    ]
    
    all_ok = True
    for module, name in deps_to_check:
        success, _ = run_command(
            f'docker exec ai-callcenter python3 -c "import {module}"',
            check_output=True
        )
        
        if success:
            print(f"  {Colors.GREEN}✓ {name}{Colors.END}")
        else:
            print(f"  {Colors.RED}✗ {name} не установлен{Colors.END}")
            all_ok = False
    
    return all_ok


def test_config():
    """Проверка конфигурации"""
    print(f"\n{Colors.BLUE}⚙️  Проверка конфигурации...{Colors.END}")
    
    config_file = Path("config.json")
    env_file = Path(".env")
    
    if config_file.exists():
        print(f"  {Colors.GREEN}✓ config.json существует{Colors.END}")
    else:
        print(f"  {Colors.RED}✗ config.json не найден{Colors.END}")
        return False
    
    if env_file.exists():
        print(f"  {Colors.GREEN}✓ .env существует{Colors.END}")
    else:
        print(f"  {Colors.RED}✗ .env не найден{Colors.END}")
        return False
    
    # Проверка конфигов Asterisk
    pjsip_conf = Path("asterisk/configs/pjsip.conf")
    extensions_conf = Path("asterisk/configs/extensions.conf")
    
    if pjsip_conf.exists():
        print(f"  {Colors.GREEN}✓ pjsip.conf существует{Colors.END}")
    else:
        print(f"  {Colors.RED}✗ pjsip.conf не найден{Colors.END}")
        return False
    
    if extensions_conf.exists():
        print(f"  {Colors.GREEN}✓ extensions.conf существует{Colors.END}")
    else:
        print(f"  {Colors.RED}✗ extensions.conf не найден{Colors.END}")
        return False
    
    return True


def test_logs():
    """Проверка логов"""
    print(f"\n{Colors.BLUE}📊 Проверка логов...{Colors.END}")
    
    logs_dir = Path("logs")
    
    if logs_dir.exists():
        print(f"  {Colors.GREEN}✓ Директория логов существует{Colors.END}")
        
        # Проверка последних логов AGI
        agi_logs = list(Path("logs/agi").glob("agi_*.log")) if (logs_dir / "agi").exists() else []
        if agi_logs:
            latest_log = max(agi_logs, key=lambda p: p.stat().st_mtime)
            print(f"  {Colors.GREEN}✓ Последний лог AGI: {latest_log.name}{Colors.END}")
        else:
            print(f"  {Colors.YELLOW}⚠ Логи AGI пока не созданы{Colors.END}")
        
        return True
    else:
        print(f"  {Colors.YELLOW}⚠ Директория логов не найдена{Colors.END}")
        return True  # Не критично


def print_summary(results):
    """Вывод итогов"""
    print(f"\n{'='*60}")
    print(f"{Colors.BOLD}📋 ИТОГИ ТЕСТИРОВАНИЯ{Colors.END}")
    print(f"{'='*60}\n")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✓ PASSED{Colors.END}" if result else f"{Colors.RED}✗ FAILED{Colors.END}"
        print(f"  {test_name:<30} {status}")
    
    print(f"\n{'='*60}")
    print(f"  Пройдено: {Colors.GREEN}{passed}/{total}{Colors.END}")
    print(f"  Провалено: {Colors.RED}{failed}/{total}{Colors.END}")
    print(f"{'='*60}\n")
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!{Colors.END}\n")
        print(f"{Colors.BLUE}Система готова к работе!{Colors.END}")
        print(f"{Colors.BLUE}Настройте MicroSIP и звоните!{Colors.END}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  Некоторые тесты не пройдены{Colors.END}\n")
        print(f"{Colors.BLUE}Проверьте логи: docker-compose logs -f{Colors.END}\n")


def main():
    """Главная функция"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}  🧪 ТЕСТИРОВАНИЕ AI CALL CENTER{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    results = {}
    
    # Запуск тестов
    results["Docker"] = test_docker()
    results["Контейнер"] = test_container()
    
    if results["Контейнер"]:
        results["Asterisk"] = test_asterisk()
        results["AGI скрипт"] = test_agi_script()
        results["Python зависимости"] = test_python_deps()
    
    results["Конфигурация"] = test_config()
    results["Логи"] = test_logs()
    
    # Итоги
    print_summary(results)
    
    # Возвращаем код выхода
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Тестирование прервано{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Ошибка: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
