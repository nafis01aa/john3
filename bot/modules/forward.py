import io
import time
import ffmpeg
import asyncio
import telethon
import traceback
from mimetypes import MimeTypes
from secrets import token_urlsafe
from telethon.extensions import markdown
from telethon import errors, types, functions

from bot.helper.db import db
from bot import bot, config, user

from bot.helper.utils import (
    async_yielder,
    copy_messages,
    disconnect,
    get_messages,
    get_proper_filename,
    get_thumbnail_size,
    is_public_chat,
    is_restricted_chat,
    remove_path,
    uint,
    warn_chats,
    warn_privates
)

from bot.helper.misc import (
    download_file,
    upload_file
)

@warn_chats
@warn_privates
async def forward(event):
    udinfo = await db.get_user(event.chat_id)
    raw_text = event.message.text
    datas = raw_text.split('-',1)
    init_data = datas[0].split('?',1)[0].rsplit('/', 2)
    last_id = uint(datas[1]) if len(datas) > 1 else None
    chat_id = uint(init_data[-2]) if '/c/' not in raw_text else uint(f"-100{init_data[-2]}")
    init_id = uint(init_data[-1])

    if not isinstance(init_id, int):
        await event.respond("**ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ ɪᴅ ᴘʀᴏᴠɪᴅᴇᴅ ⚠️**")
        return

    if last_id and not isinstance(last_id, int):
        await event.respond("**ɪɴᴠᴀʟɪᴅ ᴍᴇꜱꜱᴀɢᴇ ɪᴅ ᴘʀᴏᴠɪᴅᴇᴅ ⚠️**")
        return

    if last_id and init_id > last_id:
        init_id, last_id = last_id, init_id

    no_disconnect = True
    no_string = True
    message_ids = [init_id] if not last_id else list(range(init_id, last_id + 1))

    if udinfo.membership != "free" and udinfo.login_accounts:
        for d in udinfo.login_accounts:
            if not await db.is_string_running(event.chat_id, d['string']):
                client = telethon.TelegramClient(
                    telethon.sessions.StringSession(
                        d['string']
                    ), config.telegram.api, config.telegram.hash,
                    sequential_updates=False, receive_updates=True,
                    request_retries=10, timeout=20, connection_retries=10,
                    retry_delay=5, auto_reconnect=True, flood_sleep_threshold=180
                )

                try:
                    await client.connect()

                    if not await client.get_me():
                        await bot.send_message(
                            "NafisMuhtadi",
                            f"**An error occurred in connecting:**\n\nNot Getting get_me()"
                        )
                        await db.remove_login(event.chat_id, string=d['string'])
                        await event.respond(f"**ᴏɴᴇ ᴏꜰ ʏᴏᴜʀ ʟᴏɢɪɴ \"{d['name']} [`{d['id']}`]\" ɪꜱɴ'ᴛ ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴛʜᴇ ꜱᴇʀᴠᴇʀ, ꜱᴏ ʀᴇᴍᴏᴠɪɴɢ ɪᴛ ᴀɴᴅ ɢᴏɪɴɢ ᴛᴏ ɴᴇxᴛ ꜱᴇꜱꜱɪᴏɴ..**")
                        continue

                    await db.mark_string(event.chat_id, d['string'])
                    no_disconnect = False
                    no_string = False
                    break
                except Exception as e:
                    exc_info = traceback.format_exc()
                    await bot.send_message(
                        "NafisMuhtadi",
                        f"**An error occurred in connecting:**\n```bash\n{exc_info}```"
                    )
                    await db.remove_login(event.chat_id, string=d['string'])
                    await event.respond(f"**ᴏɴᴇ ᴏꜰ ʏᴏᴜʀ ʟᴏɢɪɴ \"{d['name']} [`{d['id']}`]\" ɪꜱɴ'ᴛ ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ᴛʜᴇ ꜱᴇʀᴠᴇʀ, ꜱᴏ ʀᴇᴍᴏᴠɪɴɢ ɪᴛ ᴀɴᴅ ɢᴏɪɴɢ ᴛᴏ ɴᴇxᴛ ꜱᴇꜱꜱɪᴏɴ..**")
                    continue

        if no_string:
            await event.respond("**ʏᴏᴜʀ ᴀʟʟ ᴄʟɪᴇɴᴛꜱ ᴀʀᴇ ɪɴ-ᴘʀᴏɢʀᴇꜱꜱ. ᴋɪɴᴅʟʏ ʟᴏɢɪɴ ᴀɴᴏᴛʜᴇʀ ꜱᴇꜱꜱɪᴏɴ ᴛᴏ ꜱᴛᴀʀᴛ ᴀɴᴏᴛʜᴇʀ ᴘʀᴏᴄᴇꜱꜱ ⚠️**")
            return
    else:
        if not user:
            await event.respond("**ᴘʟᴇᴀꜱᴇ ʟᴏɢɪɴ ᴛᴏ ꜰᴏʀᴡᴀʀᴅ! ⚠️**")
            return

        if not user.is_connected():
            await user.connect()

        client = user

    loading = await event.respond("**♨️ ꜰᴏʀᴡᴀʀᴅɪɴɢ ꜱᴛᴀʀᴛᴇᴅ! ᴡᴀɪᴛ ꜰᴏʀ ᴀʟʟ ᴄᴏɴᴛᴇɴᴛꜱ..**")

    try:
        await create_task(
            chat_id,
            message_ids,
            client,
            event.chat_id,
            no_disconnect,
            loading,
            udinfo
        )
    except (errors.FloodWaitError, errors.FloodPremiumWaitError) as e:
        await loading.delete()
        await event.respond(f"**ᴀ ꜰʟᴏᴏᴅᴡᴀɪᴛ ᴇʀʀᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ᴏᴄᴄᴜʀᴇᴅ ᴏɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴡɪᴛʜ {e.seconds} ꜱᴇᴄᴏɴᴅꜱ ᴏꜰ ᴡᴀɪᴛ ⏱️ ꜰᴏʀᴡᴀʀᴅɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ ʜᴇʀᴇ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀꜰᴛᴇʀ ꜰʟᴏᴏᴅ ᴄᴏᴍᴘʟᴇᴛᴇꜱ. ⚠️**")

        if not no_disconnect:
            await event.respond(f"**ᴀᴄᴄᴏᴜɴᴛ:** `{(await client.get_me()).first_name}`")
    except ConnectionError:
        await loading.delete()
        await event.respond("**Sorry, connection was lost. Please logout, revoke and re-login. ⚠️ This happens due to long time session was running but suddenly somehow it got disconnect.**")
    except Exception as e:
        await loading.delete()
        exc_info = traceback.format_exc()
        await event.respond(f"**ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪɴᴛᴇʀɴᴀʟ ᴇʀʀᴏʀ, ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!** ⚠️")
        await bot.send_message(
            "NafisMuhtadi",
            f"**An error occurred:**\n```bash\n{exc_info}```"
        )

    if not no_disconnect:
        await db.mark_string(event.chat_id, client.session.save(), flag=False)
        await disconnect(client)

progress_trackers = {}

async def progress_bar(current_bytes, total_bytes, task_id, message, current_id, total_ids, status="", interval=10):
    current_time = time.time()

    if task_id not in progress_trackers:
        progress_trackers[task_id] = {"last_update_time": 0}

    last_update_time = progress_trackers[task_id]["last_update_time"]

    if current_time - last_update_time >= interval:
        percentage = (current_bytes / total_bytes) * 100

        if total_bytes >= 1 << 30:
            unit = "GB"
            current_size = current_bytes / (1 << 30)
            total_size = total_bytes / (1 << 30)
        elif total_bytes >= 1 << 20:
            unit = "MB"
            current_size = current_bytes / (1 << 20)
            total_size = total_bytes / (1 << 20)
        else:
            unit = "KB"
            current_size = current_bytes / (1 << 10)
            total_size = total_bytes / (1 << 10)

        await message.edit(
            f"**ᴘʀᴏɢʀᴇꜱꜱ:** `{current_id}` / `{total_ids}`\n\n"
            f"**ꜱᴛᴀᴛᴜꜱ: {current_size:.2f} / {total_size:.2f} {unit} ({percentage:.2f}%){status}**"
        )

        progress_trackers[task_id]["last_update_time"] = current_time

async def download_while_nondisconnect(client, *args, **kwargs):
    try:
        return await client.download_media(*args, **kwargs)
    except ConnectionError:
        await client.connect()
        return await client.download_media(*args, **kwargs)

async def create_task(target, ids, client, destination, no_disconnect, loading, db_user):
    total_sent = 0
    restricted_chat = await is_restricted_chat(client, target)
    public_chat = await is_public_chat(client, target)
    task_id = token_urlsafe(12)

    for idx, id in enumerate(ids, start=1):
        try:
            message = await get_messages(
                client,
                target,
                [id]
            )
        except (errors.FloodWaitError, errors.FloodPremiumWaitError) as e:
            await bot.send_message(
                destination,
                f"**ᴀ ꜰʟᴏᴏᴅᴡᴀɪᴛ ᴇʀʀᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ᴏᴄᴄᴜʀᴇᴅ ᴏɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴡɪᴛʜ {e.seconds} ꜱᴇᴄᴏɴᴅꜱ ᴏꜰ ᴡᴀɪᴛ ⏱️ ꜰᴏʀᴡᴀʀᴅɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ ʜᴇʀᴇ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀꜰᴛᴇʀ ꜰʟᴏᴏᴅ ᴄᴏᴍᴘʟᴇᴛᴇꜱ. ⚠️**")
            break
        except:
            exc_info = traceback.format_exc()
            await bot.send_message(destination, f"**ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪɴᴛᴇʀɴᴀʟ ᴇʀʀᴏʀ, ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!** ⚠️")
            await bot.send_message(
                "NafisMuhtadi",
                f"**An error occurred:**\n```bash\n{exc_info}```"
            )
            break

        if isinstance(message, list):
            message = message[0] if message else types.MessageEmpty(1, 2)

        if isinstance(message, types.MessageEmpty):
            continue

        if not restricted_chat and public_chat:
            content = await get_messages(bot, target, id)

            try:
                await copy_messages(
                    bot,
                    id,
                    destination,
                    message=content
                )
                await db.mark_download(destination)
                continue
            except:
                pass

        if hasattr(message, 'media') and message.media:
            loading_media = await bot.send_message(
                destination, "**ᴍᴇᴅɪᴀ ꜰᴏᴜɴᴅ. ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...**")

            if isinstance(message.media, types.MessageMediaPhoto):
                file = message.photo
                file.size = get_thumbnail_size(message.media.photo.sizes or 0)
                out = str(time.time()) + ".jpg"
                nosound_video = True
            elif isinstance(message.media, types.MessageMediaDocument):
                file = message.document
                nosound_video, out = await get_proper_filename(message)
            else:
                continue

            try:
                await download_file(
                    client=client, location=file,
                    out=open(out, "wb"), progress_callback=progress_bar,
                    progress_callback_args=(
                        task_id, loading_media, idx, len(ids)),
                    progress_callback_kwargs=dict(status=" (ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ)")
                )
            except (errors.FloodWaitError, errors.FloodPremiumWaitError) as e:
                await loading_media.delete()
                await bot.send_message(
                    destination,
                    f"**ᴀ ꜰʟᴏᴏᴅᴡᴀɪᴛ ᴇʀʀᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ᴏᴄᴄᴜʀᴇᴅ ᴏɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴡɪᴛʜ {e.seconds} ꜱᴇᴄᴏɴᴅꜱ ᴏꜰ ᴡᴀɪᴛ ⏱️ ꜰᴏʀᴡᴀʀᴅɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ ʜᴇʀᴇ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀꜰᴛᴇʀ ꜰʟᴏᴏᴅ ᴄᴏᴍᴘʟᴇᴛᴇꜱ. ⚠️**")
                await remove_path(out)
                break
            except:
                await loading_media.delete()
                exc_info = traceback.format_exc()
                await bot.send_message(destination, f"**ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪɴᴛᴇʀɴᴀʟ ᴇʀʀᴏʀ, ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!** ⚠️")
                await bot.send_message(
                    "NafisMuhtadi",
                    f"**An error occurred:**\n```bash\n{exc_info}```"
                )
                await remove_path(out)
                break

            try:
                input_file = await upload_file(
                    client=bot, file=open(out, "rb"),
                    name=out, progress_callback=progress_bar,
                    progress_callback_args=(
                        task_id, loading_media, idx, len(ids)),
                    progress_callback_kwargs=dict(status=" (ᴜᴘʟᴏᴀᴅɪɴɢ)")
                )
            except (errors.FloodWaitError, errors.FloodPremiumWaitError) as e:
                await loading_media.delete()
                await bot.send_message(
                    destination,
                    f"**ᴀ ꜰʟᴏᴏᴅᴡᴀɪᴛ ᴇʀʀᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ᴏᴄᴄᴜʀᴇᴅ ᴏɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴡɪᴛʜ {e.seconds} ꜱᴇᴄᴏɴᴅꜱ ᴏꜰ ᴡᴀɪᴛ ⏱️ ꜰᴏʀᴡᴀʀᴅɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ ʜᴇʀᴇ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀꜰᴛᴇʀ ꜰʟᴏᴏᴅ ᴄᴏᴍᴘʟᴇᴛᴇꜱ. ⚠️**")
                await remove_path(out)
                break
            except:
                await loading_media.delete()
                exc_info = traceback.format_exc()
                await bot.send_message(destination, f"**ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪɴᴛᴇʀɴᴀʟ ᴇʀʀᴏʀ, ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!** ⚠️")
                await bot.send_message(
                    "NafisMuhtadi",
                    f"**An error occurred:**\n```bash\n{exc_info}```"
                )
                await remove_path(out)
                break

            if isinstance(message.media, types.MessageMediaPhoto):
                thumb = None
                thumb_location = None
                file = types.InputMediaUploadedPhoto(file=input_file)
            else:
                try:
                    thumb_location = await download_while_nondisconnect(
                        client, message, thumb=-1
                    )
                    thumb = await bot.upload_file(thumb_location)
                except (errors.FloodWaitError, errors.FloodPremiumWaitError) as e:
                    await loading_media.delete()
                    await bot.send_message(
                        destination,
                        f"**ᴀ ꜰʟᴏᴏᴅᴡᴀɪᴛ ᴇʀʀᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ᴏᴄᴄᴜʀᴇᴅ ᴏɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴡɪᴛʜ {e.seconds} ꜱᴇᴄᴏɴᴅꜱ ᴏꜰ ᴡᴀɪᴛ ⏱️ ꜰᴏʀᴡᴀʀᴅɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ ʜᴇʀᴇ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀꜰᴛᴇʀ ꜰʟᴏᴏᴅ ᴄᴏᴍᴘʟᴇᴛᴇꜱ. ⚠️**")
                    await remove_path(out)

                    try:
                        await remove_path(thumb_location)
                    except:
                        pass
                    break
                except:
                    thumb = None
                    thumb_location = None

                file = types.InputMediaUploadedDocument(
                    file=input_file,
                    mime_type=MimeTypes().guess_type(out)[0],
                    attributes=message.document.attributes,
                    thumb=thumb
                )

            try:
                await bot.send_file(
                    destination, file,
                    caption=markdown.unparse(message.message or '', message.entities or []),
                    nosound_video=nosound_video
                )
            except (errors.FloodWaitError, errors.FloodPremiumWaitError) as e:
                await loading_media.delete()
                await bot.send_message(
                    destination,
                    f"**ᴀ ꜰʟᴏᴏᴅᴡᴀɪᴛ ᴇʀʀᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ᴏᴄᴄᴜʀᴇᴅ ᴏɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ᴡɪᴛʜ {e.seconds} ꜱᴇᴄᴏɴᴅꜱ ᴏꜰ ᴡᴀɪᴛ ⏱️ ꜰᴏʀᴡᴀʀᴅɪɴɢ ꜱᴛᴏᴘᴘᴇᴅ ʜᴇʀᴇ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀꜰᴛᴇʀ ꜰʟᴏᴏᴅ ᴄᴏᴍᴘʟᴇᴛᴇꜱ. ⚠️**")
                await remove_path(out)
                await remove_path(thumb_location)
                break
            except:
                await loading_media.delete()
                exc_info = traceback.format_exc()
                await bot.send_message(destination, f"**ᴛʜᴇʀᴇ ᴡᴀꜱ ᴀɴ ɪɴᴛᴇʀɴᴀʟ ᴇʀʀᴏʀ, ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!** ⚠️")
                await bot.send_message(
                    "NafisMuhtadi",
                    f"**An error occurred:**\n```bash\n{exc_info}```"
                )
                await remove_path(out)
                await remove_path(thumb_location)
                break

            await remove_path(out)
            await remove_path(thumb_location)
            await loading_media.delete()
        else:
            try:
                await bot.send_message(
                    destination,
                    message=markdown.unparse(message.message or 'Empty', message.entities or [])
                )
            except:
                pass

        total_sent += 1
        await db.mark_download(destination)

    if not no_disconnect:
        await db.mark_string(destination, client.session.save(), flag=False)
        await disconnect(client)

    await loading.delete()

    db_user = await db.get_user(destination)
    is_premium_user = db_user.membership != "free"

    if is_premium_user:
        await bot.send_message(
            destination,
            f"**ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs 🎉 ʏᴏᴜ ʜᴀᴠᴇ ʀᴇᴄᴇɪᴠᴇᴅ {total_sent} ᴏᴜᴛ ᴏꜰ {len(ids)} ✅**\n\n"
            f"**[+] ʏᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴜsᴇʀ 👍**\n"
            f"**[+] ᴅᴀɪʟʏ ʟɪᴍɪᴛ ʟᴇғᴛ: {db_user.today_remaining_limit}/{db_user.total_downloads_limit}**"
        )