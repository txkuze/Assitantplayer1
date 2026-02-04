import asyncio
import logging
import os
import tempfile
from typing import Optional, Dict
import wave
import threading
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)

class AudioCaptureManager:
    def __init__(self):
        self.capturing: Dict[int, bool] = {}
        self.capture_threads: Dict[int, threading.Thread] = {}
        self.audio_buffers: Dict[int, list] = {}

    def is_capturing(self, chat_id: int) -> bool:
        return self.capturing.get(chat_id, False)

    def start_capture(self, chat_id: int):
        if self.is_capturing(chat_id):
            logger.info(f"Already capturing audio for chat {chat_id}")
            return

        self.capturing[chat_id] = True
        self.audio_buffers[chat_id] = []
        logger.info(f"Started audio capture for chat {chat_id}")

    def stop_capture(self, chat_id: int):
        if chat_id in self.capturing:
            self.capturing[chat_id] = False

        if chat_id in self.audio_buffers:
            del self.audio_buffers[chat_id]

        logger.info(f"Stopped audio capture for chat {chat_id}")

    async def process_audio_chunk(self, chat_id: int, audio_data: bytes):
        if not self.is_capturing(chat_id):
            return

        if chat_id not in self.audio_buffers:
            self.audio_buffers[chat_id] = []

        self.audio_buffers[chat_id].append(audio_data)

    async def get_audio_file(self, chat_id: int) -> Optional[str]:
        if chat_id not in self.audio_buffers or not self.audio_buffers[chat_id]:
            return None

        try:
            temp_dir = config.VOICE_CACHE_DIR
            os.makedirs(temp_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = os.path.join(temp_dir, f"capture_{chat_id}_{timestamp}.wav")

            audio_data = b''.join(self.audio_buffers[chat_id])

            with wave.open(audio_file, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(48000)
                wf.writeframes(audio_data)

            self.audio_buffers[chat_id] = []

            return audio_file

        except Exception as e:
            logger.error(f"Error creating audio file for chat {chat_id}: {e}")
            return None

audio_capture_manager = AudioCaptureManager()
