import asyncio
import logging
import os
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from config import config
from database.mongodb import db
from handlers import commands, voice_chat, music, group_management
from utils.logger import send_startup_log
from utils.generate_silence import generate_silence_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MusicBot:
    def __init__(self):
        self.bot = Client(
            "music_bot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN
        )

        self.assistant = Client(
            "assistant",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.STRING_SESSION
        )

        self.start_time = datetime.now()

    async def start(self):
        try:
            os.makedirs(config.MUSIC_CACHE_DIR, exist_ok=True)
            os.makedirs(config.VOICE_CACHE_DIR, exist_ok=True)

            logger.info("Generating silence audio file for voice chat...")
            generate_silence_file()

            await db.connect()

            await self.bot.start()
            logger.info("Bot started successfully")

            await self.assistant.start()
            logger.info("Assistant started successfully")

            bot_info = await self.bot.get_me()
            assistant_info = await self.assistant.get_me()

            await send_startup_log(self.bot, bot_info, assistant_info, self.start_time)

            logger.info(f"Bot: @{bot_info.username}")
            logger.info(f"Assistant: @{assistant_info.username}")
            logger.info("Voice chat listening mode enabled")

            await asyncio.Event().wait()

        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise

    async def stop(self):
        await self.bot.stop()
        await self.assistant.stop()
        await db.close()
        logger.info("Bot stopped")

music_bot = MusicBot()

commands.setup_handlers(music_bot.bot, music_bot.assistant)
voice_chat.setup_handlers(music_bot.bot, music_bot.assistant)
music.setup_handlers(music_bot.bot, music_bot.assistant)
group_management.setup_handlers(music_bot.bot, music_bot.assistant)

if __name__ == "__main__":
    try:
        asyncio.run(music_bot.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
