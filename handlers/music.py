from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import logging
from database.mongodb import db
from utils.downloader import download_song, search_song
from utils.speech import recognize_speech
from utils.logger import log_to_group
from handlers.voice_chat import join_voice_chat, active_calls
from utils.voice_listener import voice_listener
import os

logger = logging.getLogger(__name__)

async def play_handler(client: Client, message: Message):
    await db.increment_command_usage("play")
    chat_id = message.chat.id

    if chat_id not in active_calls:
        await message.reply_text(
            "Assistant is not active in this chat!\n"
            "Use /assiststart first to activate the assistant."
        )
        return

    query = message.text.split(maxsplit=1)
    if len(query) < 2:
        await message.reply_text(
            "Please provide a song name!\n"
            "Example: /play Despacito"
        )
        return

    song_query = query[1]
    status_msg = await message.reply_text(f"Searching for: {song_query}...")

    try:
        song_info = await search_song(song_query)

        if not song_info:
            await status_msg.edit_text("Sorry, couldn't find the song!")
            return

        await status_msg.edit_text(
            f"Found: {song_info['title']}\n"
            f"Downloading..."
        )

        audio_path = await download_song(song_info['url'])

        if not audio_path:
            await status_msg.edit_text("Error downloading the song!")
            return

        await status_msg.edit_text("Starting playback...")

        assistant = client.assistant
        success = await join_voice_chat(assistant, chat_id, audio_path)

        if success:
            await status_msg.edit_text(
                f"Now Playing:\n"
                f"{song_info['title']}\n\n"
                f"Duration: {song_info.get('duration', 'Unknown')}\n"
                f"Platform: {song_info.get('platform', 'YouTube')}"
            )

            await db.add_song_play(
                song_info['title'],
                song_info.get('platform', 'YouTube'),
                chat_id
            )

            await log_to_group(
                client,
                f"**Now Playing**\n"
                f"Song: {song_info['title']}\n"
                f"Chat: {message.chat.title}\n"
                f"Requested by: {message.from_user.mention}"
            )
        else:
            await status_msg.edit_text("Error starting playback!")

    except Exception as e:
        logger.error(f"Error in play_handler: {e}")
        await status_msg.edit_text(f"Error: {str(e)}")

async def voice_message_handler(client: Client, message: Message):
    chat_id = message.chat.id

    if chat_id not in active_calls:
        return

    try:
        status_msg = await message.reply_text("Processing your voice command...")

        voice_file = await message.download()

        async def handle_command(chat_id: int, command: dict):
            await process_voice_command_from_message(client, message, command, status_msg)

        await voice_listener.process_voice_segment(chat_id, voice_file, handle_command)

        if os.path.exists(voice_file):
            os.remove(voice_file)

    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        await message.reply_text(f"Error processing voice: {str(e)}")

async def process_voice_command_from_message(client: Client, message: Message, command: dict, status_msg: Message):
    try:
        chat_id = message.chat.id
        action = command.get('action')

        if action == 'play':
            query = command.get('query', '')
            if query:
                await status_msg.edit_text(f"Playing: {query}\n\nSearching...")

                song_info = await search_song(query)

                if song_info:
                    await status_msg.edit_text(f"Found: {song_info['title']}\nDownloading...")

                    audio_path = await download_song(song_info['url'])

                    if audio_path:
                        assistant = client.assistant
                        success = await join_voice_chat(assistant, chat_id, audio_path)

                        if success:
                            await status_msg.edit_text(
                                f"Now Playing:\n{song_info['title']}\n\n"
                                f"Duration: {song_info.get('duration', 'Unknown')}\n"
                                f"Platform: {song_info.get('platform', 'YouTube')}"
                            )

                            await db.add_song_play(
                                song_info['title'],
                                song_info.get('platform', 'YouTube'),
                                chat_id
                            )

                            await log_to_group(
                                client,
                                f"**Voice Command Executed**\n"
                                f"Song: {song_info['title']}\n"
                                f"Chat: {message.chat.title}\n"
                                f"User: {message.from_user.mention}"
                            )
                        else:
                            await status_msg.edit_text("Error starting playback!")
                    else:
                        await status_msg.edit_text("Error downloading the song!")
                else:
                    await status_msg.edit_text("Sorry, couldn't find the song!")
            else:
                await status_msg.edit_text("Please specify a song name!")
        else:
            await status_msg.edit_text(
                f"Command received: {action}\n"
                f"This feature is coming soon!"
            )

    except Exception as e:
        logger.error(f"Error processing voice command from message: {e}")
        await status_msg.edit_text(f"Error: {str(e)}")

def setup_handlers(bot: Client, assistant: Client):
    bot.assistant = assistant

    bot.add_handler(filters.command("play") & filters.group, play_handler)
    bot.add_handler(filters.voice & filters.group, voice_message_handler)
