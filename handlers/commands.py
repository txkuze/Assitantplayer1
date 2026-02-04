from pyrogram import Client, filters
from pyrogram.types import Message
import psutil
import time
from datetime import datetime
from database.mongodb import db
from config import config

start_time = time.time()

async def start_handler(client: Client, message: Message):
    await db.increment_command_usage("start")
    await message.reply_text(
        f"Hello {message.from_user.mention}!\n\n"
        "I'm a powerful music bot with voice chat listening capabilities!\n\n"
        "**Available Commands:**\n"
        "/start - Start the bot\n"
        "/help - Get help\n"
        "/stats - View bot statistics\n"
        "/ping - Check bot latency\n"
        "/assiststart - Start assistant in voice chat\n"
        "/assistclose - Stop assistant from voice chat\n"
        "/play [song name] - Play a song\n\n"
        "**Voice Control:**\n"
        "Say 'Assistant play [song name]' in voice chat and I'll play it!\n"
        "The assistant listens continuously when active."
    )

async def help_handler(client: Client, message: Message):
    await db.increment_command_usage("help")
    help_text = """
**Music Bot Help**

**Basic Commands:**
/start - Start the bot
/help - Show this help message
/stats - View bot statistics
/ping - Check bot response time

**Music Commands:**
/assiststart - Start assistant and activate voice listening
/assistclose - Stop assistant from voice chat
/play [song name] - Play a song in voice chat

**Voice Chat Control:**
The assistant listens continuously when active. Just speak naturally:
- "Assistant play Challeya"
- "Assistant play Shape of You by Ed Sheeran"
- "Assistant pause"
- "Assistant resume"
- "Assistant stop"

**How to use:**
1. Add the bot to your group
2. Start or join a voice chat
3. Use /assiststart to activate voice listening
4. Speak naturally: "Assistant play [song name]"
5. Or use /play [song name] or send voice messages
6. The assistant stays active and listens for commands
7. Use /assistclose to end the session

**Supported Platforms:**
- YouTube
- Spotify
- SoundCloud
- Direct URLs

For support, contact the bot owner.
"""
    await message.reply_text(help_text)

async def stats_handler(client: Client, message: Message):
    await db.increment_command_usage("stats")

    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent

    total_plays = await db.get_total_plays()
    command_stats = await db.get_stats()
    active_chats = await db.get_active_chats()

    stats_text = f"""
**Bot Statistics**

**System:**
Uptime: {hours}h {minutes}m {seconds}s
CPU Usage: {cpu_percent}%
Memory Usage: {memory_percent}%

**Usage:**
Total Songs Played: {total_plays}
Active Chats: {len(active_chats)}
Commands Used: {sum(command_stats.values())}

**Top Commands:**
"""

    sorted_commands = sorted(command_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    for cmd, count in sorted_commands:
        stats_text += f"/{cmd}: {count}\n"

    await message.reply_text(stats_text)

async def ping_handler(client: Client, message: Message):
    await db.increment_command_usage("ping")
    start = datetime.now()
    msg = await message.reply_text("Pinging...")
    end = datetime.now()
    latency = (end - start).microseconds / 1000

    await msg.edit_text(f"**Pong!**\nLatency: `{latency}ms`")

def setup_handlers(bot: Client, assistant: Client):
    bot.add_handler(filters.command("start") & filters.private, start_handler)
    bot.add_handler(filters.command("help"), help_handler)
    bot.add_handler(filters.command("stats"), stats_handler)
    bot.add_handler(filters.command("ping"), ping_handler)
