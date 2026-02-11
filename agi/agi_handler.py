#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGI Handler для AI Call Center
Обработка звонков через Asterisk Gateway Interface
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# Настройка логирования
log_dir = Path('/var/log/agi')
log_dir.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'agi_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger('AGI_Handler')


class AGI:
    """Asterisk Gateway Interface handler"""
    
    def __init__(self):
        self.env = {}
        self.read_environment()
        
    def read_environment(self):
        """Чтение переменных окружения AGI"""
        logger.debug("Reading AGI environment...")
        
        while True:
            line = sys.stdin.readline().strip()
            if not line:
                break
            
            if ':' in line:
                key, value = line.split(':', 1)
                self.env[key.strip()] = value.strip()
        
        logger.info(f"AGI Environment: {self.env}")
    
    def execute(self, command):
        """Выполнение AGI команды"""
        sys.stdout.write(f"{command}\n")
        sys.stdout.flush()
        
        response = sys.stdin.readline().strip()
        logger.debug(f"Command: {command} | Response: {response}")
        
        return response
    
    def answer(self):
        """Ответить на звонок"""
        return self.execute('ANSWER')
    
    def stream_file(self, filename, escape_digits=''):
        """Проиграть аудио файл"""
        return self.execute(f'STREAM FILE {filename} "{escape_digits}"')
    
    def get_data(self, filename, timeout=5000, max_digits=0):
        """Получить DTMF ввод"""
        return self.execute(f'GET DATA {filename} {timeout} {max_digits}')
    
    def say_digits(self, number):
        """Произнести цифры"""
        return self.execute(f'SAY DIGITS {number} ""')
    
    def hangup(self):
        """Повесить трубку"""
        return self.execute('HANGUP')
    
    def set_variable(self, var, value):
        """Установить переменную"""
        return self.execute(f'SET VARIABLE {var} {value}')
    
    def record_file(self, filename, format='wav', escape_digits='#', timeout=-1, offset=0, beep=True, silence=None):
        """Записать аудио"""
        cmd = f'RECORD FILE {filename} {format} "{escape_digits}" {timeout} {offset} {"BEEP" if beep else ""}'
        if silence:
            cmd += f' s={silence}'
        return self.execute(cmd)
    
    def verbose(self, message, level=1):
        """Вывести сообщение в Asterisk CLI"""
        return self.execute(f'VERBOSE "{message}" {level}')


class AIEngine:
    """AI движок для обработки разговоров"""
    
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'anthropic')
        self.model = os.getenv('AI_MODEL', 'claude-sonnet-4-5-20250929')
        self.api_key = os.getenv('AI_API_KEY', '')
        self.language = os.getenv('AI_LANGUAGE', 'русский')
        
        logger.info(f"AI Engine initialized: {self.provider} / {self.model}")
    
    def chat(self, message: str, conversation_history: list = None) -> str:
        """Отправка сообщения в AI"""
        try:
            if self.provider == 'anthropic':
                return self._chat_anthropic(message, conversation_history)
            elif self.provider == 'openai':
                return self._chat_openai(message, conversation_history)
            elif self.provider == 'google':
                return self._chat_google(message)
            elif self.provider == 'ollama':
                return self._chat_ollama(message)
            else:
                return "Извините, AI провайдер не настроен."
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return "Извините, произошла ошибка при обработке запроса."
    
    def _chat_anthropic(self, message: str, conversation_history: list = None) -> str:
        """Anthropic Claude"""
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.api_key)
            
            messages = conversation_history or []
            messages.append({
                "role": "user",
                "content": message
            })
            
            system_prompt = os.getenv('AI_SYSTEM_PROMPT', 
                f'Вы вежливый AI-ассистент колл-центра. Отвечайте на {self.language} языке, кратко и по делу.')
            
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            raise
    
    def _chat_openai(self, message: str, conversation_history: list = None) -> str:
        """OpenAI GPT"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            messages = [
                {
                    "role": "system",
                    "content": os.getenv('AI_SYSTEM_PROMPT', 
                        f'Вы вежливый AI-ассистент колл-центра. Отвечайте на {self.language} языке.')
                }
            ]
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({
                "role": "user",
                "content": message
            })
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise
    
    def _chat_google(self, message: str) -> str:
        """Google Gemini"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            response = model.generate_content(message)
            return response.text
            
        except Exception as e:
            logger.error(f"Google error: {e}")
            raise
    
    def _chat_ollama(self, message: str) -> str:
        """Ollama локальная модель"""
        try:
            import requests
            
            ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
            
            response = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": message,
                    "stream": False
                }
            )
            
            return response.json()['response']
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise


class VoiceEngine:
    """Голосовой движок: TTS и STT"""
    
    def __init__(self):
        self.tts_provider = os.getenv('TTS_PROVIDER', 'google')
        self.stt_provider = os.getenv('STT_PROVIDER', 'google')
        self.temp_dir = Path('/tmp/agi_audio')
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Voice Engine: TTS={self.tts_provider}, STT={self.stt_provider}")
    
    def text_to_speech(self, text: str, output_file: str) -> bool:
        """Преобразование текста в речь"""
        try:
            if self.tts_provider == 'google':
                return self._tts_google(text, output_file)
            elif self.tts_provider == 'yandex':
                return self._tts_yandex(text, output_file)
            elif self.tts_provider == 'openai':
                return self._tts_openai(text, output_file)
            else:
                logger.error(f"Unknown TTS provider: {self.tts_provider}")
                return False
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def _tts_google(self, text: str, output_file: str) -> bool:
        """Google TTS"""
        try:
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='ru', slow=False)
            wav_file = f"{output_file}.wav"
            tts.save(wav_file)
            
            # Конвертация в формат Asterisk (8kHz, mono, ulaw)
            import subprocess
            subprocess.run([
                'sox', wav_file,
                '-r', '8000',
                '-c', '1',
                '-e', 'mu-law',
                output_file
            ], check=True)
            
            os.remove(wav_file)
            return True
            
        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return False
    
    def _tts_yandex(self, text: str, output_file: str) -> bool:
        """Yandex SpeechKit TTS"""
        try:
            import requests
            
            api_key = os.getenv('YANDEX_API_KEY')
            folder_id = os.getenv('YANDEX_FOLDER_ID')
            
            url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
            
            headers = {
                'Authorization': f'Api-Key {api_key}'
            }
            
            data = {
                'text': text,
                'lang': 'ru-RU',
                'voice': 'alena',
                'folderId': folder_id,
                'format': 'lpcm',
                'sampleRateHertz': '8000'
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                logger.error(f"Yandex TTS error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Yandex TTS error: {e}")
            return False
    
    def _tts_openai(self, text: str, output_file: str) -> bool:
        """OpenAI TTS"""
        try:
            from openai import OpenAI
            import subprocess
            
            client = OpenAI(api_key=os.getenv('AI_API_KEY'))
            
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            mp3_file = f"{output_file}.mp3"
            response.stream_to_file(mp3_file)
            
            # Конвертация в формат Asterisk
            subprocess.run([
                'sox', mp3_file,
                '-r', '8000',
                '-c', '1',
                '-e', 'mu-law',
                output_file
            ], check=True)
            
            os.remove(mp3_file)
            return True
            
        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}")
            return False
    
    def speech_to_text(self, audio_file: str) -> str:
        """Преобразование речи в текст"""
        try:
            if self.stt_provider == 'google':
                return self._stt_google(audio_file)
            elif self.stt_provider == 'yandex':
                return self._stt_yandex(audio_file)
            elif self.stt_provider == 'whisper':
                return self._stt_whisper(audio_file)
            else:
                logger.error(f"Unknown STT provider: {self.stt_provider}")
                return ""
        except Exception as e:
            logger.error(f"STT error: {e}")
            return ""
    
    def _stt_google(self, audio_file: str) -> str:
        """Google Speech-to-Text"""
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            # Конвертируем в WAV если нужно
            wav_file = f"{audio_file}.wav"
            import subprocess
            subprocess.run(['sox', audio_file, wav_file], check=True)
            
            with sr.AudioFile(wav_file) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language='ru-RU')
            
            os.remove(wav_file)
            return text
            
        except Exception as e:
            logger.error(f"Google STT error: {e}")
            return ""
    
    def _stt_yandex(self, audio_file: str) -> str:
        """Yandex SpeechKit STT"""
        try:
            import requests
            
            api_key = os.getenv('YANDEX_API_KEY')
            
            with open(audio_file, 'rb') as f:
                data = f.read()
            
            url = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
            
            headers = {
                'Authorization': f'Api-Key {api_key}'
            }
            
            params = {
                'lang': 'ru-RU',
                'format': 'lpcm',
                'sampleRateHertz': '8000'
            }
            
            response = requests.post(url, headers=headers, params=params, data=data)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result', '')
            else:
                logger.error(f"Yandex STT error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Yandex STT error: {e}")
            return ""
    
    def _stt_whisper(self, audio_file: str) -> str:
        """Whisper локальный STT"""
        # TODO: Реализовать Whisper
        logger.warning("Whisper STT not implemented yet")
        return ""


class CallHandler:
    """Обработчик звонка"""
    
    def __init__(self, agi: AGI):
        self.agi = agi
        self.ai = AIEngine()
        self.voice = VoiceEngine()
        self.conversation_history = []
        
        self.caller_id = agi.env.get('agi_callerid', 'Unknown')
        self.call_id = agi.env.get('agi_uniqueid', 'unknown')
        
        logger.info(f"New call from {self.caller_id}, ID: {self.call_id}")
    
    def handle(self):
        """Главная логика обработки звонка"""
        try:
            # Приветствие
            self.agi.verbose("Starting AI call handler", 3)
            
            greeting = "Здравствуйте! Вас приветствует AI-ассистент. Чем могу помочь?"
            self.speak(greeting)
            
            # Основной цикл разговора
            max_turns = 10
            for turn in range(max_turns):
                logger.info(f"Conversation turn {turn + 1}/{max_turns}")
                
                # Слушаем пользователя
                user_input = self.listen()
                
                if not user_input:
                    logger.warning("No input from user")
                    self.speak("Простите, я вас не расслышал. Не могли бы вы повторить?")
                    continue
                
                logger.info(f"User said: {user_input}")
                
                # Проверка на завершение
                if any(word in user_input.lower() for word in ['до свидания', 'пока', 'спасибо', 'всё']):
                    self.speak("Спасибо за звонок! До свидания!")
                    break
                
                # Отправляем в AI
                ai_response = self.ai.chat(user_input, self.conversation_history)
                logger.info(f"AI response: {ai_response}")
                
                # Обновляем историю
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                # Говорим ответ
                self.speak(ai_response)
            
            # Прощание
            self.speak("Хорошего дня!")
            
        except Exception as e:
            logger.error(f"Call handling error: {e}", exc_info=True)
            self.speak("Извините, произошла ошибка. До свидания.")
        
        finally:
            self.agi.hangup()
    
    def speak(self, text: str):
        """Произнести текст"""
        logger.debug(f"Speaking: {text}")
        
        # Генерируем аудио файл
        audio_file = self.voice.temp_dir / f"tts_{self.call_id}_{datetime.now().timestamp()}"
        
        if self.voice.text_to_speech(text, str(audio_file)):
            # Проигрываем через Asterisk
            self.agi.stream_file(str(audio_file), '')
            
            # Удаляем временный файл
            try:
                os.remove(audio_file)
            except:
                pass
        else:
            logger.error("Failed to generate speech")
    
    def listen(self, timeout=5) -> str:
        """Слушать пользователя и распознать речь"""
        logger.debug("Listening for user input...")
        
        # Записываем аудио
        audio_file = self.voice.temp_dir / f"rec_{self.call_id}_{datetime.now().timestamp()}"
        
        # Записываем с таймаутом тишины
        self.agi.record_file(
            str(audio_file),
            format='wav',
            escape_digits='#',
            timeout=timeout * 1000,
            beep=False,
            silence=2
        )
        
        # Распознаём речь
        audio_path = f"{audio_file}.wav"
        text = self.voice.speech_to_text(audio_path)
        
        # Удаляем временный файл
        try:
            os.remove(audio_path)
        except:
            pass
        
        return text


def main():
    """Точка входа AGI скрипта"""
    try:
        logger.info("="*60)
        logger.info("AGI Script started")
        logger.info("="*60)
        
        # Создаём AGI интерфейс
        agi = AGI()
        
        # Ответить на звонок
        agi.answer()
        
        # Обработка звонка
        handler = CallHandler(agi)
        handler.handle()
        
        logger.info("Call completed successfully")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
