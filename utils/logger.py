from pyrogram import Client
from datetime import datetime
from config import config
import logging
import platform
import psutil

logger = logging.getLogger(__name__)

async def send_startup_log(bot: Client, bot_info, assistant_info, start_time):
    try:
        if not config.LOGGER_GROUP_ID or config.LOGGER_GROUP_ID == 0:
            logger.warning("LOGGER_GROUP_ID not configured, skipping startup log")
            return

        system_info = f"""
**Bot Started Successfully**

**Bot Information:**
Name: {bot_info.first_name}
Username: @{bot_info.username}
ID: `{bot_info.id}`

**Assistant Information:**
Name: {assistant_info.first_name}
Username: @{assistant_info.username}
ID: `{assistant_info.id}`

**System Information:**
Platform: {platform.system()} {platform.release()}
Python: {platform.python_version()}
CPU Cores: {psutil.cpu_count()}
RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB

**Start Time:**
{start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}

Bot is now running and ready to serve!
"""

        await bot.send_message(
            config.LOGGER_GROUP_ID,
            system_info
        )
        logger.info("Startup log sent to logger group")

    except Exception as e:
        logger.error(f"Failed to send startup log: {e}")
        logger.error(f"Make sure LOGGER_GROUP_ID ({config.LOGGER_GROUP_ID}) is correct and bot is added to the group as admin")

async def log_to_group(bot: Client, message: str):
    try:
        if not config.LOGGER_GROUP_ID or config.LOGGER_GROUP_ID == 0:
            return

        await bot.send_message(
            config.LOGGER_GROUP_ID,
            message
        )
    except Exception as e:
        logger.error(f"Failed to send log to group: {e}")
