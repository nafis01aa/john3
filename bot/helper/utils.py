import re
import os
import time
import aiofiles
import aioshutil
import aiofiles.os
import phonenumbers
from functools import wraps
from contextlib import suppress
from telethon import errors, functions, types

from bot import bot, config
from bot.helper.db import db
from bot.helper.state import states
from bot.helper.button import button
from bot.helper.commands import command

def uint(i, method='int'):
    try:
        return eval(method)(i)
    except:
        return i

def get_name(p):
    if p.last_name:
        return "{} {}".format(
            p.first_name,
            p.last_name
        )
    return p.first_name

def is_valid_phone(phone):
    try:
        if phone.startswith('+'):
            parsed_number = phonenumbers.parse(phone)
            return phonenumbers.is_valid_number(parsed_number)
        return False
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

def get_thumbnail_size(thumbs):
    size = 0

    for thumb in thumbs:
        if size:
            return size
        if isinstance(thumb, types.PhotoSize):
            size = thumb.size
        if isinstance(thumb, types.VideoSize):
            size = thumb.size
        if isinstance(thumb, types.PhotoStrippedSize):
            size = len(thumb.bytes)
        if isinstance(thumb, types.PhotoCachedSize):
            size = len(thumb.bytes)
        if isinstance(thumb, types.PhotoSizeProgressive):
            size = max(thumb.sizes)
    return size

def only_admin(callback):
    @wraps(callback)
    async def wrapper(event, *args, **kwargs):
        sender = await event.get_sender()
        if sender and sender.id in [config.owner.id] + config.owner.admins:
            await callback(event, *args, **kwargs)
    return wrapper

def warn_privates(callback):
    @wraps(callback)
    async def wrapper(event, *args, **kwargs):
        sender = await event.get_sender()
        udinfo = await db.get_user(sender.id)
        if udinfo.membership == "free":
            if '/c/' in event.message.text:
                await event.respond("**ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴘʀɪᴠᴀᴛᴇ ᴄᴏɴᴛᴇɴᴛꜱ! ⚠️**")
                return
        await callback(event, *args, **kwargs)
    return wrapper

def warn_chats(callback):
    @wraps(callback)
    async def wrapper(event, *args, **kwargs):
        if not event.is_private:
            await event.reply(
                "**ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴘʀɪᴍᴀʀɪʟʏ ᴅᴇꜱɪɢɴᴇᴅ ꜰᴏʀ ᴜꜱɪɴɢ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛꜱ.**")
            return
        await callback(event, *args, **kwargs)
    return wrapper

def check_cancel(callback):
    @wraps(callback)
    async def wrapper(event, *args, **kwargs):
        if not event.message.text:
            return

        if event.message.text and \
            event.message.text == command.cancel_menu:
                app = await states.get_data(event.chat_id, 'app')
                await disconnect(app)
                await states.finish(event.chat_id)
                await event.respond(
                    "ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘʀᴏᴄᴇꜱꜱ ʜᴀꜱ ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.❗",
                    buttons=button.remove()
                )
                return
        await callback(event, *args, **kwargs)
    return wrapper

def resolve_tg_link(link):
    if link.startswith("@"):
        return link.strip('@')

    if (
        link.isdigit() or
        link.startswith("-")
    ):
        return int(link)

    username = link.strip(
        '/'
    ).split(
        '?',
        1
    )[0].rsplit(
        '/',
        1
    )[-1]
    return username.strip('@')

def to_small_caps(text):
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ',
        'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ',
        'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
        's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ',
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ',
        'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ',
        'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ',
        'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x',
        'Y': 'ʏ', 'Z': 'ᴢ',
        '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
        '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
    }

    matches = list(re.finditer(r'{.*?}|\n|\\.', text))
    ignored_parts = {match.span(): match.group() for match in matches}

    result = []
    i = 0
    while i < len(text):
        if any(start <= i < end for start, end in ignored_parts):
            for (start, end), value in ignored_parts.items():
                if start == i:
                    result.append(value)
                    i = end
                    break
        else:
            result.append(small_caps.get(text[i], text[i]))
            i += 1

    return ''.join(result)

async def reorder_handlers():
    bot._event_builders.sort(key=lambda x: not hasattr(x[0], 'func') or not x[0].func)

async def disconnect(app):
    with suppress(Exception):
        await app.disconnect()

async def async_yielder(items):
    for i in items:
        yield i

async def remove_path(path):
    if await aiofiles.os.path.isfile(str(path)):
        try:
            await aiofiles.os.remove(str(path))
        except:
            pass
    elif await aiofiles.os.path.isdir(str(path)):
        try:
            await aioshutil.rmtree(str(path))
        except:
            pass

async def get_messages(app, chat_id, ids):
    try:
        peer = await app.get_input_entity(chat_id)
        messages = await app(functions.channels.GetMessagesRequest(peer, ids if isinstance(ids, list) else [ids]))
        return messages.messages if isinstance(ids, list) and len(ids) > 1 else messages.messages[0]
    except Exception as e:
        print(e)
        return []

async def get_proper_filename(message):
    filename = next(
        (attr for attr in message.file.media.attributes if isinstance(attr, types.DocumentAttributeFilename)),
        None
    )

    if filename:
        return True, filename.file_name

    if message.file.name:
        return True, message.file.name

    for attr in message.file.media.attributes:
        if isinstance(attr, types.DocumentAttributeAnimated):
            return False, str(time.time()) + ".gif"
        elif isinstance(attr, types.DocumentAttributeAudio):
            return True, str(time.time()) + ".mp3"
        elif isinstance(attr, types.DocumentAttributeCustomEmoji):
            return True, str(time.time()) + ".tgs"
        elif isinstance(attr, types.DocumentAttributeSticker):
            return True, str(time.time()) + ".tgs"
        elif isinstance(attr, types.DocumentAttributeVideo):
            return True, str(time.time()) + ".mp4"
        elif isinstance(attr, types.DocumentAttributeImageSize):
            return True, str(time.time()) + ".jpg"

    return True, str(time.time()) + ".jpg"

async def copy_messages(app, ids, to_chat_id=None, from_chat_id=None, drop_author=True, message=None):
    await app(
        functions.messages.ForwardMessagesRequest(
            from_peer=await app.get_input_entity(message.chat_id if message else from_chat_id),
            id=ids if isinstance(ids, list) else [ids],
            to_peer=await app.get_input_entity(to_chat_id),
            drop_author=drop_author
        )
    )

async def get_full_chat(app, chat_id):
    try:
        full_chat = await app(functions.channels.GetFullChannelRequest(chat_id))

        for chat in full_chat.chats:
            if chat.id == full_chat.full_chat.id:
                return chat

        return None
    except Exception as e:
        print(e)
        return None

async def is_restricted_chat(app, chat_id):
    full_chat = await get_full_chat(app, chat_id)
    return getattr(full_chat, 'noforwards', False)

async def is_public_chat(app, chat_id):
    with suppress(Exception):
        entity = await app.get_entity(chat_id)
        return bool(entity.username)
    return False

async def is_canceled(conv, text):
    if text and command.cancel_menu in text:
        await conv.send_message(
            "ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘʀᴏᴄᴇꜱꜱ ʜᴀꜱ ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.❗",
            buttons=button.remove()
        )
        return True
    return False

async def is_otp(conv, text, buttons):
    if not str(text).startswith("otp"):
        await conv.send_message("⚠️ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ! ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴏᴛᴘ ᴀɢᴀɪɴ. (ᴇ.ɢ. ᴏᴛᴘ34512)", buttons=buttons)
        return False

    digits = re.findall(r'\d+', text)

    if not digits:
        await conv.send_message("⚠️ ɪɴᴠᴀʟɪᴅ ᴏᴛᴘ! ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴏᴛᴘ ᴀɢᴀɪɴ. (ᴇ.ɢ. ᴏᴛᴘ34512)", buttons=buttons)
        return False

    otp_str = ''.join(digits)
    return otp_str[:5]

async def send_code(conv, phone, app, loader, buttons):
    if loader:
        await loader.delete()

    try:
        code = await app.send_code_request(phone=phone)
        await conv.send_message("ᴘʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴏᴛᴘ 👇", buttons=buttons)
        return code
    except (errors.ApiIdInvalidError, errors.PhoneNumberInvalidError):
        await conv.send_message("ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪs ɪɴᴠᴀʟɪᴅ ❌", buttons=button.remove())
    except Exception as e:
        await conv.send_message(str(e), buttons=button.remove())

    return False

async def sign_in(conv, app, **kwargs):
    otp = kwargs.get("otp", None)
    hash = kwargs.get("hash", None)
    phone = kwargs.get("phone", None)
    password = kwargs.get("password", None)
    buttons = kwargs.get("buttons", None)

    try:
        await app.sign_in(
            phone=phone,
            code=otp,
            password=password
        )
        return True, ''
    except errors.PhoneCodeInvalidError:
        await conv.send_message("⚠️ ᴏᴛᴘ ɪꜱ ɪɴᴠᴀʟɪᴅ. ᴛʀʏ ᴀɢᴀɪɴ 👇", buttons=buttons)
        return False, 'invalid_otp'
    except errors.PhoneCodeExpiredError:
        await conv.send_message("⚠️ ᴏᴛᴘ ɪꜱ ᴇxᴘɪʀᴇᴅ.", buttons=button.remove())
        return False, 'otp_expired'
    except errors.SessionPasswordNeededError:
        await conv.send_message("2ꜰᴀ ʀᴇQᴜɪʀᴇᴅ. ꜱᴇɴᴅ ʏᴏᴜʀ ᴘᴀꜱꜱᴡᴏʀᴅ ɴᴏᴡ 👇", buttons=buttons)
        return False, 'password_required'
    except errors.PasswordHashInvalidError:
        await conv.send_message("⚠️ ɪɴᴠᴀʟɪᴅ ᴘᴀꜱꜱᴡᴏʀᴅ. ᴛʀʏ ᴀɢᴀɪɴ 👇", buttons=buttons)
        return False, 'invalid_password'

async def new_sign_in(conv, app, chat_id):
    string = app.session.save()
    me = await app.get_me()
    await db.add_new_login(
        chat_id,
        name=get_name(me),
        id=me.id,
        string=string
    )
    await disconnect(app)
    await conv.send_message(
        f"**ʏᴏᴜ ʜᴀᴠᴇ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ "
        f"ʟᴏɢɪɴᴇᴅ ✔️**\n\n"
        f"**ɴᴀᴍᴇ:** `{get_name(me)}`\n"
        f"**ɪᴅ:** `{me.id}`",
        buttons=button.remove()
    )

async def set_bot_commands(
    commands):
    bot_commands = []

    for cmd, dc in commands:
        bot_commands.append(
            types.BotCommand(
                cmd,
                dc
            )
        )

    await bot(
        functions.bots.SetBotCommandsRequest(
            scope=types.BotCommandScopeDefault(),
            lang_code='',
            commands=bot_commands
        )
    )