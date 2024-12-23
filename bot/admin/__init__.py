from telethon import events

from bot import bot
from bot.helper.state import states
from bot.helper.commands import admin_command

async def load_admin_modules():
    # Promote
    from .promote import promote, demote
    bot.add_event_handler(promote, event=events.NewMessage(pattern=admin_command.promote))
    bot.add_event_handler(demote, event=events.NewMessage(pattern=admin_command.demote))
