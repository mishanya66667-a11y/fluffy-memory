#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGI Handler для AI Call Center - OPTIMIZED FOR SPEED
Groq + Faster-Whisper = 🚀
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path
import tempfile
import subprocess

# Настройка логирования
log_dir = Path('/var/log/agi')
log_dir.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
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
        while True:
            line = sys.stdin.readline().strip()
            if not line:
                break
            if ':' in line:
                key, value = line.split(':', 1)
                self.env[key.strip()] = value.strip()
    
    def execute(self, command):
        """Выполнение AGI команды"""
        sys.stdout.write(f"{command}\n")
        sys.stdout.flush()
        response = sys.stdin.readline().strip()
        return response
    
    def answer(self):
        return self.execute('ANSWER')
    
    def stream_file(self, filename, escape_digits=''):
        return self.execute(f'STREAM FILE {filename} "{escape_digits}"')
    
    def hangup(self):
        return self.execute('HANGUP')
    
    def record_file(self, filename, format='wav', escape_digits='#', timeout=-1, beep=False, silence=2):
        cmd = f'RECORD FILE {filename} {format} "{escape_digits}" {timeout} 0'
        if beep:
            cmd += ' BEEP'
        cmd += f' s={silence}'
        return self.execute(cmd)
    
    def verbose(self, message, level=1):
        return self.execute(f'VERBOSE "{message}" {level}')


class GroqAI:
    """Groq AI - самый быстрый LLM провайдер"""
    
    def __init__(self):
        from groq import Groq
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = os.getenv('AI_MODEL', 'llama-3.1-8b-instant')
        self.language = os.getenv('AI_LANGUAGE', 'русский')
        self.system_prompt = os.getenv('AI_SYSTEM_PROMPT', 
            f'Вы вежливый AI-ассистент колл-центра. Отвечайте на {self.language} языке, кратко и по делу.')
        logger.info(f"Groq AI initialized: {self.model}")
    
    def chat(self, message: str, history: list = None) -> str:
        """Быстрый чат с Groq"""
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            if history:
                messages.extend(history)
            
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=512,  # Короче = быстрее
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return "Извините, произошла ошибка."


class FastWhisper:
    """Faster-Whisper - оптимизированный STT"""
    
    def __init__(self):
        from faster_whisper import WhisperModel
        
        model_size = os.getenv('WHISPER_MODEL', 'base')
        device = os.getenv('WHISPER_DEVICE', 'cpu')
        compute_type = os.getenv('WHISPER_COMPUTE_TYPE', 'int8')
        
        logger.info(f"Loading Faster-Whisper: {model_size} on {device} ({compute_type})")
        
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            num_workers=2
        )
        
        logger.info("Faster-Whisper ready!")
    
    def transcribe(self, audio_file: str) -> str:
        """Быстрое распознавание речи"""
        try:
            # Конвертируем в WAV 16kHz mono если нужно
            wav_file = f"{audio_file}_16k.wav"
            subprocess.run([
                'sox', audio_file,
                '-r', '16000',
                '-c', '1',
                wav_file
            ], check=True, capture_output=True)
            
            # Распознаём с VAD для пропуска тишины
            segments, info = self.model.transcribe(
                wav_file,
                language="ru",
                vad_filter=True,
                vad_parameters=dict(
                    threshold=0.5,
                    min_speech_duration_ms=250
                )
            )
            
            # Собираем текст
            text = " ".join([segment.text for segment in segments]).strip()
            
            # Удаляем временный файл
            try:
                os.remove(wav_file)
            except:
                pass
            
            return text
            
        except Exception as e:
            logger.error(f"Whisper error: {e}")
            return ""


class GroqTTS:
    """Groq TTS через API (если доступен) или fallback на gTTS"""
    
    def __init__(self):
        self.groq_client = None
        try:
            from groq import Groq
            self.groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            logger.info("Groq TTS initialized")
        except:
            logger.info("Groq TTS unavailable, using gTTS")
            self.use_gtts = True
    
    def speak(self, text: str, output_file: str) -> bool:
        """Генерация речи"""
        try:
            # Попробуем Groq TTS (если API поддерживает)
            if self.groq_client and hasattr(self.groq_client, 'audio'):
                return self._speak_groq(text, output_file)
            else:
                # Fallback на быструю gTTS
                return self._speak_gtts(text, output_file)
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False
    
    def _speak_groq(self, text: str, output_file: str) -> bool:
        """Groq TTS"""
        try:
            response = self.groq_client.audio.speech.create(
                model="whisper-large-v3-turbo",  # Если есть TTS модель
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
            ], check=True, capture_output=True)
            
            os.remove(mp3_file)
            return True
        except:
            return self._speak_gtts(text, output_file)
    
    def _speak_gtts(self, text: str, output_file: str) -> bool:
        """Fast gTTS fallback"""
        try:
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='ru', slow=False)
            mp3_file = f"{output_file}.mp3"
            tts.save(mp3_file)
            
            # Конвертация для Asterisk
            subprocess.run([
                'sox', mp3_file,
                '-r', '8000',
                '-c', '1',
                '-e', 'mu-law',
                output_file
            ], check=True, capture_output=True)
            
            os.remove(mp3_file)
            return True
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return False


class SpeedCallHandler:
    """Обработчик звонка - ОПТИМИЗИРОВАН НА СКОРОСТЬ"""
    
    def __init__(self, agi: AGI):
        self.agi = agi
        self.ai = GroqAI()
        self.stt = FastWhisper()
        self.tts = GroqTTS()
        self.history = []
        
        self.caller_id = agi.env.get('agi_callerid', 'Unknown')
        self.call_id = agi.env.get('agi_uniqueid', 'unknown')
        self.temp_dir = Path(tempfile.gettempdir()) / 'agi_speed'
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Call from {self.caller_id}")
    
    def handle(self):
        """Быстрая обработка звонка"""
        try:
            self.agi.verbose("Speed AI Call Handler", 3)
            
            # Быстрое приветствие
            self.speak("Здравствуйте! AI-ассистент. Слушаю вас.")
            
            # Основной цикл - максимум 8 реплик
            for turn in range(8):
                # Слушаем (с коротким таймаутом)
                user_text = self.listen(timeout=4)
                
                if not user_text:
                    self.speak("Не слышу вас. Повторите?")
                    continue
                
                logger.info(f"User: {user_text}")
                
                # Проверка на завершение
                exit_words = ['до свидания', 'пока', 'спасибо', 'всё', 'хватит']
                if any(word in user_text.lower() for word in exit_words):
                    self.speak("Спасибо за звонок! До свидания!")
                    break
                
                # Получаем ответ от AI
                ai_response = self.ai.chat(user_text, self.history)
                logger.info(f"AI: {ai_response}")
                
                # Обновляем историю
                self.history.append({"role": "user", "content": user_text})
                self.history.append({"role": "assistant", "content": ai_response})
                
                # Отвечаем
                self.speak(ai_response)
            
            self.speak("Хорошего дня!")
            
        except Exception as e:
            logger.error(f"Call error: {e}")
            self.speak("Извините, ошибка. До свидания.")
        finally:
            self.agi.hangup()
    
    def speak(self, text: str):
        """Быстрая генерация и проигрывание речи"""
        audio_file = self.temp_dir / f"tts_{self.call_id}_{int(datetime.now().timestamp())}"
        
        if self.tts.speak(text, str(audio_file)):
            self.agi.stream_file(str(audio_file), '')
            try:
                os.remove(audio_file)
            except:
                pass
    
    def listen(self, timeout=4) -> str:
        """Быстрое распознавание речи"""
        audio_file = self.temp_dir / f"rec_{self.call_id}_{int(datetime.now().timestamp())}"
        
        # Записываем с коротким таймаутом тишины
        self.agi.record_file(
            str(audio_file),
            format='wav',
            escape_digits='#',
            timeout=timeout * 1000,
            beep=False,
            silence=2
        )
        
        # Распознаём
        audio_path = f"{audio_file}.wav"
        text = self.stt.transcribe(audio_path)
        
        # Удаляем
        try:
            os.remove(audio_path)
        except:
            pass
        
        return text


def main():
    """Точка входа"""
    try:
        logger.info("="*60)
        logger.info("SPEED AI CALL CENTER")
        logger.info("="*60)
        
        agi = AGI()
        agi.answer()
        
        handler = SpeedCallHandler(agi)
        handler.handle()
        
        logger.info("Call completed")
        
    except Exception as e:
        logger.error(f"Fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
