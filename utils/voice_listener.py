import asyncio
import logging
import os
import tempfile
from typing import Optional, Callable, Dict
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
import re

logger = logging.getLogger(__name__)

class VoiceChatListener:
    def __init__(self):
        self.active_listeners: Dict[int, bool] = {}
        self.listener_tasks: Dict[int, asyncio.Task] = {}
        self.wake_words = ['assistant', 'hey assistant', 'ok assistant', 'hello assistant']
        self.recognizer = sr.Recognizer()

    def is_listening(self, chat_id: int) -> bool:
        return self.active_listeners.get(chat_id, False)

    async def start_listening(self, chat_id: int, command_handler: Callable):
        if chat_id in self.active_listeners and self.active_listeners[chat_id]:
            logger.info(f"Already listening in chat {chat_id}")
            return

        self.active_listeners[chat_id] = True
        task = asyncio.create_task(self._listen_loop(chat_id, command_handler))
        self.listener_tasks[chat_id] = task
        logger.info(f"Started voice listening for chat {chat_id}")

    async def stop_listening(self, chat_id: int):
        if chat_id in self.active_listeners:
            self.active_listeners[chat_id] = False

        if chat_id in self.listener_tasks:
            task = self.listener_tasks[chat_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.listener_tasks[chat_id]

        logger.info(f"Stopped voice listening for chat {chat_id}")

    async def _listen_loop(self, chat_id: int, command_handler: Callable):
        logger.info(f"Voice listening loop started for chat {chat_id}")

        while self.active_listeners.get(chat_id, False):
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in listen loop for chat {chat_id}: {e}")
                await asyncio.sleep(5)

    async def process_voice_segment(self, chat_id: int, audio_file_path: str, command_handler: Callable):
        try:
            if not self.is_listening(chat_id):
                return

            text = await self._recognize_speech(audio_file_path)

            if text:
                logger.info(f"Recognized in voice chat {chat_id}: {text}")

                command = self._extract_command(text)

                if command:
                    logger.info(f"Extracted command in chat {chat_id}: {command}")
                    await command_handler(chat_id, command)

        except Exception as e:
            logger.error(f"Error processing voice segment for chat {chat_id}: {e}")

    async def _recognize_speech(self, audio_file_path: str) -> Optional[str]:
        try:
            audio = AudioSegment.from_file(audio_file_path)

            wav_path = audio_file_path.replace(os.path.splitext(audio_file_path)[1], '.wav')
            audio.export(wav_path, format='wav')

            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)

                try:
                    text = self.recognizer.recognize_google(audio_data)

                    if os.path.exists(wav_path):
                        os.remove(wav_path)

                    return text.lower()

                except sr.UnknownValueError:
                    return None
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    return None
                finally:
                    if os.path.exists(wav_path):
                        try:
                            os.remove(wav_path)
                        except:
                            pass

        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return None

    def _extract_command(self, text: str) -> Optional[Dict]:
        text = text.lower().strip()

        wake_word_found = False
        for wake_word in self.wake_words:
            if wake_word in text:
                wake_word_found = True
                text = text.replace(wake_word, '', 1).strip()
                break

        if not wake_word_found:
            return None

        command_patterns = [
            (r'play\s+(.+)', 'play'),
            (r'search\s+(.+)', 'play'),
            (r'start\s+(.+)', 'play'),
            (r'put\s+on\s+(.+)', 'play'),
            (r'listen\s+to\s+(.+)', 'play'),
            (r'pause|hold', 'pause'),
            (r'resume|continue|unpause', 'resume'),
            (r'stop|end|quit|close', 'stop'),
            (r'skip|next', 'skip'),
            (r'volume\s+(\d+)', 'volume'),
        ]

        for pattern, action in command_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if action == 'play' and match.groups():
                    query = match.group(1).strip()
                    return {
                        'action': 'play',
                        'query': query
                    }
                elif action == 'volume' and match.groups():
                    volume = int(match.group(1))
                    return {
                        'action': 'volume',
                        'level': volume
                    }
                else:
                    return {
                        'action': action
                    }

        if text:
            return {
                'action': 'play',
                'query': text
            }

        return None

voice_listener = VoiceChatListener()
