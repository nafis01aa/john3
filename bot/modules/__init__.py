from telethon import events

from bot import bot
from bot.helper.state import states
from bot.helper.commands import command

async def load_modules():
    # Login
    from .login import login
    bot.add_event_handler(login, event=events.NewMessage(pattern=command.login))

    # Forward
    from .forward import forward
    bot.add_event_handler(forward, event=events.NewMessage(pattern=command.forward_menu))

    # Log Out
    from .logout import logout, logout_b
    bot.add_event_handler(logout, event=events.NewMessage(pattern=command.logout))
    bot.add_event_handler(logout_b, event=events.CallbackQuery(pattern=r'^logout:'))