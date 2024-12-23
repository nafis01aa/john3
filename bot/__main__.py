from telethon import events, types
from telethon.tl.custom.button import Button

from bot.helper.db import db
from bot.helper.state import states
from bot.helper.button import button
from bot.modules import load_modules
from bot.admin import load_admin_modules
from bot.helper.commands import command

from bot import (
    bot,
    bot_username,
    config,
    logger
)

from bot.helper.utils import (
    reorder_handlers,
    set_bot_commands,
    warn_chats
)

@warn_chats
async def start(event):
    text, buttons = button.start(event)
    await event.respond(text, buttons=buttons)
    await db.update_user(event.chat_id)

@warn_chats
async def help(event):
    text = (
        f"**ʜᴇʟᴘ:**\n\n"
        f"/ᴘʟᴀɴꜱ - ᴘᴜʀᴄʜᴀꜱᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ\n"
        f"/ᴘʀᴏꜰɪʟᴇ - ꜱᴇᴇ ʏᴏᴜʀ ᴘʀᴏꜰɪʟᴇ ꜱᴛᴀᴛᴜꜱ\n"
        f"/ᴛʜᴜᴍʙɴᴀɪʟ - ꜱᴇᴛ ᴏʀ ʀᴇᴍᴏᴠᴇ ᴛʜᴜᴍʙɴᴀɪʟ\n"
        f"/ʟᴏɢɪɴ - ʟᴏɢɪɴ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ ᴀɴᴅ ᴅᴏᴡɴʟᴏᴀᴅ ꜰʀᴏᴍ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟ/ɢʀᴏᴜᴘ\n"
        f"/ʟᴏɢᴏᴜᴛ - ʟᴏɢᴏᴜᴛ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ꜰʀᴏᴍ ʙᴏᴛ"
    )
    await event.respond(text)

async def main():
    await set_bot_commands(command.get_bot_commands())
    bot.add_event_handler(start, event=events.NewMessage(pattern=command.start))
    bot.add_event_handler(help, event=events.NewMessage(pattern=command.help))
    await load_modules()
    await load_admin_modules()
    await reorder_handlers()
    logger.info(f"@{bot_username} started successfully! 💥")

bot.loop.run_until_complete(main())
bot.run_until_disconnected()