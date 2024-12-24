from bot import bot
from bot.helper.db import db
from bot.helper.button import button
from bot.helper.commands import command
from bot.helper.utils import warn_chats

@warn_chats
async def logout(event):
    user = await db.get_user(event.chat_id)

    if user.membership == "free":
        await event.respond("**You are free user. You don't have permission to do this ⚠️**")
        return

    if not user.login_accounts:
        await event.respond("**You have no previously loginned accounts ⚠️**")
        return

    markup = button()

    for i, account in enumerate(user.login_accounts, start=1):
        markup.inline(
            f"{i}. {account['name']}",
            f"logout:{i}:{account['id']}"
        )

    markup.inline(command.cancel_menu, 'logout:delete_query', position='footer')
    text = "**Select to log out 👇**"
    await event.respond(text, buttons=markup.build(2))

@warn_chats
async def logout_b(event):
    pid = event.data.decode().split(':',2)[-1]

    if 'delete_query' in pid:
        await event.delete()
        return

    idx = event.data.decode().split(':',2)[1]
    await db.remove_login(event.chat_id, id=int(pid), idx=idx)
    await event.edit("**Log Out Successful** ✅")