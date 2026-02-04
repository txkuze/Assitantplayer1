from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import AudioPiped, VideoParameters, AudioParameters
from pytgcalls.exceptions import GroupCallNotFound, NotInGroupCallError
import asyncio
import logging
import os
from config import config
from database.mongodb import db
from utils.logger import log_to_group
from utils.voice_listener import voice_listener
from utils.audio_capture import audio_capture_manager

logger = logging.getLogger(__name__)

active_calls = {}
pytgcalls_instances = {}
listening_tasks = {}

async def assiststart_handler(client: Client, message: Message):
    await db.increment_command_usage("assiststart")
    chat_id = message.chat.id

    try:
        status_msg = await message.reply_text("Starting assistant and joining voice chat...")

        try:
            assistant = client.assistant
            await assistant.join_chat(chat_id)
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            logger.error(f"Error joining chat: {e}")

        await db.add_chat(chat_id, message.chat.title)

        if chat_id not in pytgcalls_instances:
            pytgcalls = PyTgCalls(assistant)
            pytgcalls_instances[chat_id] = pytgcalls
            await pytgcalls.start()

        pytgcalls = pytgcalls_instances[chat_id]

        try:
            await pytgcalls.join_group_call(
                chat_id,
                AudioPiped(
                    os.path.join(config.VOICE_CACHE_DIR, "silence.mp3")
                ) if os.path.exists(os.path.join(config.VOICE_CACHE_DIR, "silence.mp3")) else None,
                stream_type=StreamType().pulse_stream
            )
            active_calls[chat_id] = True
            logger.info(f"Assistant joined voice chat in {chat_id}")
        except Exception as e:
            logger.error(f"Error joining voice chat: {e}")

        async def handle_voice_command(chat_id: int, command: dict):
            await process_voice_command(client, chat_id, command)

        await voice_listener.start_listening(chat_id, handle_voice_command)
        audio_capture_manager.start_capture(chat_id)

        await status_msg.edit_text(
            "Assistant is now active in voice chat!\n\n"
            "I'm listening for your commands. Say:\n"
            "- 'Assistant play [song name]' to play music\n"
            "- 'Assistant pause' to pause\n"
            "- 'Assistant resume' to resume\n"
            "- 'Assistant stop' to stop\n\n"
            "Just speak naturally in the voice chat!"
        )

        await log_to_group(
            client,
            f"**Assistant Started & Listening**\n"
            f"Chat: {message.chat.title}\n"
            f"Chat ID: {chat_id}\n"
            f"Started by: {message.from_user.mention}\n"
            f"Voice recognition: Active"
        )

        listening_tasks[chat_id] = asyncio.create_task(
            voice_listening_loop(client, chat_id)
        )

    except Exception as e:
        logger.error(f"Error in assiststart: {e}")
        await message.reply_text(f"Error starting assistant: {str(e)}")

async def assistclose_handler(client: Client, message: Message):
    await db.increment_command_usage("assistclose")
    chat_id = message.chat.id

    try:
        await voice_listener.stop_listening(chat_id)
        audio_capture_manager.stop_capture(chat_id)

        if chat_id in listening_tasks:
            task = listening_tasks[chat_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del listening_tasks[chat_id]

        if chat_id in pytgcalls_instances:
            pytgcalls = pytgcalls_instances[chat_id]
            try:
                await pytgcalls.leave_group_call(chat_id)
            except (GroupCallNotFound, NotInGroupCallError):
                pass

            del pytgcalls_instances[chat_id]

        if chat_id in active_calls:
            del active_calls[chat_id]

        await db.remove_chat(chat_id)

        await message.reply_text("Assistant left the voice chat and stopped listening. Goodbye!")

        await log_to_group(
            client,
            f"**Assistant Stopped**\n"
            f"Chat: {message.chat.title}\n"
            f"Chat ID: {chat_id}\n"
            f"Stopped by: {message.from_user.mention}"
        )

    except Exception as e:
        logger.error(f"Error in assistclose: {e}")
        await message.reply_text(f"Error closing assistant: {str(e)}")

async def join_voice_chat(assistant: Client, chat_id: int, audio_path: str):
    try:
        if chat_id not in pytgcalls_instances:
            pytgcalls = PyTgCalls(assistant)
            pytgcalls_instances[chat_id] = pytgcalls
            await pytgcalls.start()

        pytgcalls = pytgcalls_instances[chat_id]

        await pytgcalls.join_group_call(
            chat_id,
            AudioPiped(audio_path),
            stream_type=StreamType().pulse_stream
        )

        active_calls[chat_id] = True
        return True

    except Exception as e:
        logger.error(f"Error joining voice chat: {e}")
        return False

async def leave_voice_chat(chat_id: int):
    try:
        if chat_id in pytgcalls_instances:
            pytgcalls = pytgcalls_instances[chat_id]
            await pytgcalls.leave_group_call(chat_id)

        if chat_id in active_calls:
            del active_calls[chat_id]

        return True

    except Exception as e:
        logger.error(f"Error leaving voice chat: {e}")
        return False

async def voice_listening_loop(client: Client, chat_id: int):
    logger.info(f"Started voice listening loop for chat {chat_id}")

    try:
        while voice_listener.is_listening(chat_id):
            await asyncio.sleep(2)

    except asyncio.CancelledError:
        logger.info(f"Voice listening loop cancelled for chat {chat_id}")
    except Exception as e:
        logger.error(f"Error in voice listening loop for chat {chat_id}: {e}")

async def process_voice_command(client: Client, chat_id: int, command: dict):
    try:
        action = command.get('action')
        logger.info(f"Processing voice command in chat {chat_id}: {action}")

        if action == 'play':
            query = command.get('query', '')
            if query:
                from utils.downloader import download_song, search_song

                song_info = await search_song(query)

                if song_info:
                    logger.info(f"Found song: {song_info['title']} for voice command")

                    audio_path = await download_song(song_info['url'])

                    if audio_path:
                        assistant = client.assistant
                        success = await join_voice_chat(assistant, chat_id, audio_path)

                        if success:
                            logger.info(f"Now playing {song_info['title']} in chat {chat_id}")

                            await db.add_song_play(
                                song_info['title'],
                                song_info.get('platform', 'YouTube'),
                                chat_id
                            )

                            await log_to_group(
                                client,
                                f"**Voice Command Executed**\n"
                                f"Command: Play\n"
                                f"Song: {song_info['title']}\n"
                                f"Chat ID: {chat_id}"
                            )

        elif action == 'pause':
            logger.info(f"Pause command received in chat {chat_id}")

        elif action == 'resume':
            logger.info(f"Resume command received in chat {chat_id}")

        elif action == 'stop':
            await leave_voice_chat(chat_id)
            logger.info(f"Stop command received in chat {chat_id}")

    except Exception as e:
        logger.error(f"Error processing voice command in chat {chat_id}: {e}")

def setup_handlers(bot: Client, assistant: Client):
    bot.assistant = assistant

    bot.add_handler(filters.command("assiststart") & filters.group, assiststart_handler)
    bot.add_handler(filters.command("assistclose") & filters.group, assistclose_handler)
