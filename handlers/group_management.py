from pyrogram import Client, filters
from pyrogram.types import Message, ChatPrivileges
from pyrogram.handlers import MessageHandler
from pyrogram.errors import (
    UserAdminInvalid, ChatAdminRequired, UserNotParticipant,
    BadRequest, FloodWait
)
import asyncio
import logging
from datetime import datetime, timedelta
from database.mongodb import db
from utils.logger import log_to_group

logger = logging.getLogger(__name__)

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ["creator", "administrator"]
    except Exception:
        return False

async def ban_handler(client: Client, message: Message):
    await db.increment_command_usage("ban")
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("You need to be an admin to use this command!")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to ban them!")
        return

    target_user = message.reply_to_message.from_user

    if await is_admin(client, chat_id, target_user.id):
        await message.reply_text("Cannot ban an admin!")
        return

    try:
        await client.ban_chat_member(chat_id, target_user.id)
        await message.reply_text(
            f"User {target_user.mention} has been banned!"
        )

        await log_to_group(
            client,
            f"**User Banned**\n"
            f"Chat: {message.chat.title}\n"
            f"Banned User: {target_user.mention} ({target_user.id})\n"
            f"Banned By: {message.from_user.mention}"
        )

    except ChatAdminRequired:
        await message.reply_text("I need admin rights to ban users!")
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def unban_handler(client: Client, message: Message):
    await db.increment_command_usage("unban")
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("You need to be an admin to use this command!")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to unban them!")
        return

    target_user = message.reply_to_message.from_user

    try:
        await client.unban_chat_member(chat_id, target_user.id)
        await message.reply_text(
            f"User {target_user.mention} has been unbanned!"
        )

        await log_to_group(
            client,
            f"**User Unbanned**\n"
            f"Chat: {message.chat.title}\n"
            f"Unbanned User: {target_user.mention} ({target_user.id})\n"
            f"Unbanned By: {message.from_user.mention}"
        )

    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def kick_handler(client: Client, message: Message):
    await db.increment_command_usage("kick")
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("You need to be an admin to use this command!")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to kick them!")
        return

    target_user = message.reply_to_message.from_user

    if await is_admin(client, chat_id, target_user.id):
        await message.reply_text("Cannot kick an admin!")
        return

    try:
        await client.ban_chat_member(chat_id, target_user.id)
        await asyncio.sleep(1)
        await client.unban_chat_member(chat_id, target_user.id)

        await message.reply_text(
            f"User {target_user.mention} has been kicked!"
        )

        await log_to_group(
            client,
            f"**User Kicked**\n"
            f"Chat: {message.chat.title}\n"
            f"Kicked User: {target_user.mention} ({target_user.id})\n"
            f"Kicked By: {message.from_user.mention}"
        )

    except ChatAdminRequired:
        await message.reply_text("I need admin rights to kick users!")
    except Exception as e:
        logger.error(f"Error kicking user: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def mute_handler(client: Client, message: Message):
    await db.increment_command_usage("mute")
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("You need to be an admin to use this command!")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to mute them!")
        return

    target_user = message.reply_to_message.from_user

    if await is_admin(client, chat_id, target_user.id):
        await message.reply_text("Cannot mute an admin!")
        return

    try:
        await client.restrict_chat_member(
            chat_id,
            target_user.id,
            ChatPrivileges(can_send_messages=False)
        )

        await message.reply_text(
            f"User {target_user.mention} has been muted!"
        )

        await log_to_group(
            client,
            f"**User Muted**\n"
            f"Chat: {message.chat.title}\n"
            f"Muted User: {target_user.mention} ({target_user.id})\n"
            f"Muted By: {message.from_user.mention}"
        )

    except ChatAdminRequired:
        await message.reply_text("I need admin rights to mute users!")
    except Exception as e:
        logger.error(f"Error muting user: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def unmute_handler(client: Client, message: Message):
    await db.increment_command_usage("unmute")
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("You need to be an admin to use this command!")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to unmute them!")
        return

    target_user = message.reply_to_message.from_user

    try:
        await client.restrict_chat_member(
            chat_id,
            target_user.id,
            ChatPrivileges(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
        )

        await message.reply_text(
            f"User {target_user.mention} has been unmuted!"
        )

        await log_to_group(
            client,
            f"**User Unmuted**\n"
            f"Chat: {message.chat.title}\n"
            f"Unmuted User: {target_user.mention} ({target_user.id})\n"
            f"Unmuted By: {message.from_user.mention}"
        )

    except Exception as e:
        logger.error(f"Error unmuting user: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def promote_handler(client: Client, message: Message):
    await db.increment_command_usage("promote")
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await client.get_chat_member(chat_id, user_id)
    if member.status != "creator":
        await message.reply_text("Only the group creator can promote users!")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to promote them!")
        return

    target_user = message.reply_to_message.from_user

    try:
        await client.promote_chat_member(
            chat_id,
            target_user.id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=False,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True
            )
        )

        await message.reply_text(
            f"User {target_user.mention} has been promoted to admin!"
        )

        await log_to_group(
            client,
            f"**User Promoted**\n"
            f"Chat: {message.chat.title}\n"
            f"Promoted User: {target_user.mention} ({target_user.id})\n"
            f"Promoted By: {message.from_user.mention}"
        )

    except ChatAdminRequired:
        await message.reply_text("I need admin rights to promote users!")
    except Exception as e:
        logger.error(f"Error promoting user: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def demote_handler(client: Client, message: Message):
    await db.increment_command_usage("demote")
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await client.get_chat_member(chat_id, user_id)
    if member.status != "creator":
        await message.reply_text("Only the group creator can demote users!")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a user's message to demote them!")
        return

    target_user = message.reply_to_message.from_user

    try:
        await client.promote_chat_member(
            chat_id,
            target_user.id,
            privileges=ChatPrivileges(
                can_manage_chat=False,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
        )

        await message.reply_text(
            f"User {target_user.mention} has been demoted!"
        )

        await log_to_group(
            client,
            f"**User Demoted**\n"
            f"Chat: {message.chat.title}\n"
            f"Demoted User: {target_user.mention} ({target_user.id})\n"
            f"Demoted By: {message.from_user.mention}"
        )

    except Exception as e:
        logger.error(f"Error demoting user: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def pin_handler(client: Client, message: Message):
    await db.increment_command_usage("pin")
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("You need to be an admin to use this command!")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a message to pin it!")
        return

    try:
        await client.pin_chat_message(
            chat_id,
            message.reply_to_message.id
        )

        await message.reply_text("Message pinned successfully!")

    except ChatAdminRequired:
        await message.reply_text("I need admin rights to pin messages!")
    except Exception as e:
        logger.error(f"Error pinning message: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def unpin_handler(client: Client, message: Message):
    await db.increment_command_usage("unpin")
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("You need to be an admin to use this command!")
        return

    try:
        if message.reply_to_message:
            await client.unpin_chat_message(
                chat_id,
                message.reply_to_message.id
            )
        else:
            await client.unpin_all_chat_messages(chat_id)

        await message.reply_text("Message(s) unpinned successfully!")

    except ChatAdminRequired:
        await message.reply_text("I need admin rights to unpin messages!")
    except Exception as e:
        logger.error(f"Error unpinning message: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def purge_handler(client: Client, message: Message):
    await db.increment_command_usage("purge")
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await message.reply_text("You need to be an admin to use this command!")
        return

    if not message.reply_to_message:
        await message.reply_text("Reply to a message to purge from!")
        return

    try:
        status = await message.reply_text("Purging messages...")

        start_id = message.reply_to_message.id
        end_id = message.id

        message_ids = list(range(start_id, end_id + 1))

        await client.delete_messages(chat_id, message_ids)

        await asyncio.sleep(2)
        await status.delete()

        await log_to_group(
            client,
            f"**Messages Purged**\n"
            f"Chat: {message.chat.title}\n"
            f"Count: {len(message_ids)}\n"
            f"Purged By: {message.from_user.mention}"
        )

    except ChatAdminRequired:
        await message.reply_text("I need admin rights to delete messages!")
    except Exception as e:
        logger.error(f"Error purging messages: {e}")
        await message.reply_text(f"Error: {str(e)}")

async def info_handler(client: Client, message: Message):
    await db.increment_command_usage("info")

    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user

    try:
        member = await client.get_chat_member(message.chat.id, user.id)

        info_text = f"""
**User Information**

Name: {user.mention}
User ID: `{user.id}`
Username: @{user.username if user.username else 'None'}
Status: {member.status}

**Account Details:**
First Seen: {member.joined_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(member, 'joined_date') and member.joined_date else 'Unknown'}
"""

        await message.reply_text(info_text)

    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        await message.reply_text(f"Error: {str(e)}")

def setup_handlers(bot: Client, assistant: Client):
    bot.add_handler(MessageHandler(ban_handler, filters.command("ban") & filters.group))
    bot.add_handler(MessageHandler(unban_handler, filters.command("unban") & filters.group))
    bot.add_handler(MessageHandler(kick_handler, filters.command("kick") & filters.group))
    bot.add_handler(MessageHandler(mute_handler, filters.command("mute") & filters.group))
    bot.add_handler(MessageHandler(unmute_handler, filters.command("unmute") & filters.group))
    bot.add_handler(MessageHandler(promote_handler, filters.command("promote") & filters.group))
    bot.add_handler(MessageHandler(demote_handler, filters.command("demote") & filters.group))
    bot.add_handler(MessageHandler(pin_handler, filters.command("pin") & filters.group))
    bot.add_handler(MessageHandler(unpin_handler, filters.command("unpin") & filters.group))
    bot.add_handler(MessageHandler(purge_handler, filters.command("purge") & filters.group))
    bot.add_handler(MessageHandler(info_handler, filters.command("info") & filters.group))
