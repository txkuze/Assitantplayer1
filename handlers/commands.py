from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
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
        "I'm an advanced music and group management bot with voice chat listening capabilities!\n\n"
        "**Music Commands:**\n"
        "/assiststart - Start assistant in voice chat\n"
        "/assistclose - Stop assistant from voice chat\n"
        "/play [song name] - Play a song\n\n"
        "**Group Management:**\n"
        "/ban, /kick, /mute, /promote - Manage users\n"
        "/pin, /purge, /info - Manage messages\n\n"
        "**Other Commands:**\n"
        "/help - Get detailed help\n"
        "/stats - View bot statistics\n"
        "/ping - Check bot latency\n\n"
        "**Voice Control:**\n"
        "Say 'Assistant play [song]', 'Assistant pause', 'Assistant stop' in voice chat!\n"
        "The assistant listens continuously when active."
    )

async def help_handler(client: Client, message: Message):
    await db.increment_command_usage("help")
    help_text = """
**Advanced Music & Group Management Bot**

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
The assistant listens continuously when active. Say:
- "Assistant play [song name]" - Play music
- "Assistant pause/hold" - Pause playback
- "Assistant resume/continue" - Resume playback
- "Assistant stop/end/quit" - Stop and leave voice chat
- "Assistant skip/next" - Skip current song

**Group Management Commands:**
/ban - Ban a user (reply to message)
/unban - Unban a user (reply to message)
/kick - Kick a user (reply to message)
/mute - Mute a user (reply to message)
/unmute - Unmute a user (reply to message)
/promote - Promote user to admin (reply to message)
/demote - Demote an admin (reply to message)
/pin - Pin a message (reply to message)
/unpin - Unpin message or all messages
/purge - Delete messages (reply to start message)
/info - Get user info (reply to user or use directly)

**How to use Music:**
1. Add the bot to your group
2. Make it admin with necessary permissions
3. Start or join a voice chat
4. Use /assiststart to activate voice listening
5. Speak naturally: "Assistant play [song name]"
6. Or use /play [song name] or send voice messages
7. The assistant stays active and listens
8. Use /assistclose to end the session

**Supported Platforms:**
- YouTube
- Spotify
- SoundCloud
- Direct URLs

**Admin Permissions Required:**
- Delete messages (for purge)
- Ban users (for ban/kick)
- Restrict users (for mute)
- Promote users (for promote/demote)
- Pin messages (for pin/unpin)
- Manage voice chats (for music)

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
    bot.add_handler(MessageHandler(start_handler, filters.command("start") & filters.private))
    bot.add_handler(MessageHandler(help_handler, filters.command("help")))
    bot.add_handler(MessageHandler(stats_handler, filters.command("stats")))
    bot.add_handler(MessageHandler(ping_handler, filters.command("ping")))
