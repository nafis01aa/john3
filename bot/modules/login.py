import telethon
from asyncio import exceptions
from telethon import events, errors
from telethon.sessions import StringSession

from bot import bot, config
from bot.helper.db import db
from bot.helper.state import states
from bot.helper.button import button
from bot.helper.commands import command

from bot.helper.utils import (
    check_cancel,
    disconnect,
    get_name,
    is_canceled,
    is_otp,
    is_valid_phone,
    new_sign_in,
    send_code,
    sign_in,
    warn_chats
)

@warn_chats
async def login(event):
    markup = button(False)
    markup.menu(command.cancel_menu)

    try:
        async with bot.conversation(event.chat_id, timeout=3000) as conv:
            await conv.send_message("sᴇɴᴅ ʏᴏᴜʀ ᴍᴏʙɪʟᴇ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ʙᴇʟᴏᴡ 👇", buttons=markup.build())
            phone = (await conv.get_response()).text

            while phone and not is_valid_phone(phone):
                if await is_canceled(conv, phone):
                    return

                await conv.send_message(f"⚠️ **ᴇʀʀᴏʀ:** ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴅᴇᴛᴇᴄᴛᴇᴅ. ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ **ᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ** 👇")
                phone = (await conv.get_response()).text

            loader = await bot.send_message(event.chat_id, "ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ ⏱️", buttons=button.remove())
            app = telethon.TelegramClient(
                StringSession(),
                config.telegram.api,
                config.telegram.hash,
                sequential_updates=False,
                receive_updates=False
            )

            await app.connect()
            code = await send_code(
                conv,
                phone,
                app,
                loader,
                markup.build()
            )

            if not code:
                await disconnect(app)
                return

            hash = code.phone_code_hash
            password = None
            result = None
            otp = (await conv.get_response()).text

            while not await is_otp(conv, otp, markup.build()):
                if await is_canceled(conv, otp):
                    await disconnect(app)
                    return

                otp = (await conv.get_response()).text

            signed, err = await sign_in(
                conv,
                app,
                otp=otp,
                hash=hash,
                phone=phone,
                password=password,
                buttons=markup.build()
            )

            while True:
                if await is_canceled(conv, result):
                    await disconnect(app)
                    return

                if signed:
                    return await new_sign_in(conv, app, event.chat_id)

                if 'otp_expired' in err:
                    await disconnect(app)
                    return

                if 'invalid_otp' in err:
                    result = otp = (await conv.get_response()).text
                elif 'password_required' in err:
                    otp = None
                    result = password = (await conv.get_response()).text
                elif 'invalid_password' in err:
                    result = password = (await conv.get_response()).text

                signed, err = await sign_in(
                    conv,
                    app,
                    otp=otp,
                    hash=hash,
                    phone=phone,
                    password=password
                )
    except (exceptions.TimeoutError, errors.TimeoutError):
        await event.respond("ᴛɪᴍᴇᴏᴜᴛ ᴇxᴄᴇᴇᴅᴇᴅ! ᴘʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ.❗", buttons=button.remove())