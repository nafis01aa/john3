from bot import bot, config
from bot.helper.db import db
from bot.helper.commands import command

from bot.helper.utils import (
    only_admin,
    resolve_tg_link,
    to_small_caps,
    uint
)

@only_admin
async def promote(event):
    args = event.message.text.split()

    if len(args) < 3:
        await event.respond(f"**⚠️ ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀ ɪᴅ & ᴘʟᴀɴ (1,2,3)!**")
        return

    user_id = args[1]
    plan = args[2]

    plan_data = config.get_plans_as_dict()

    if plan not in plan_data:
        supported_plans = ", ".join(f"`{i}`" for i in plan_data.keys())
        await event.respond(f"**⚠️ ɪɴᴠʟɪᴅ ᴘʟᴀɴ ᴅᴇᴛᴇᴄᴛᴇᴅ! sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʟᴀɴs ᴀʀᴇ:** {supported_plans}")
        return

    validity = plan_data[plan]['validity']
    total = uint(plan_data[plan]['mass_content_downloader'])

    try:
        user = await bot.get_entity(uint(user_id))
        user_id = user.id
    except:
        await event.respond(f"**⚠️ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ:** ɴᴇᴠᴇʀ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴘʀᴇᴠɪᴏᴜsʟʏ!")
        return

    await db.add_premium_user(
        user_id,
        membership=plan,
        total=total,
        validity=validity
    )

    await event.reply(
        f"**ᴜsᴇʀ** `{user_id}` sᴜᴄᴄᴇssғᴜʟʟʏ **ᴘʀᴏᴍᴏᴛᴇᴅ ᴛᴏ** `{plan}`! ✅"
    )

    try:
        text = (
            f"**🎉 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs!**"
            f"\n\n**ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴄᴛɪᴠᴀᴛᴇᴅ! ⚡️**"
            f"\n\n>✅ **ᴘʟᴀɴ ᴅᴇᴛᴀɪʟs: {to_small_caps(plan)} ᴘʀᴇᴍɪᴜᴍ**"
            f"\n📅 **ᴅᴜʀᴀᴛɪᴏɴ: {to_small_caps(plan_data[plan]['validity_str'])}**"
            f"\n⏳ **ᴇɴᴅɪɴɢ ᴅᴀᴛᴇ: {to_small_caps(validity.strftime('%d-%m-%Y %I:%M:%S %p'))}**>"
            f"\n\n**sᴛᴀʀᴛ ᴇɴᴊᴏʏɪɴɢ ᴀʟʟ ᴛʜᴇ ᴇxᴄʟᴜsɪᴠᴇ ғᴇᴀᴛᴜʀᴇs ᴛᴏᴅᴀʏ! 🚀**"
            f"\n\n**ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ᴄʜᴏᴏsɪɴɢ ᴜs!**"
        )

        if config.default.support:
            support_channel = resolve_tg_link(config.default.support)
            text += f" **( @{support_channel} ) !**"

        await bot.send_message(
            user_id,
            text
        )
    except:
        pass

@only_admin
async def demote(event):
    args = event.message.text.split()

    if len(args) < 2:
        await event.respond(f"**⚠️ ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀ ɪᴅ ᴛᴏ ᴅᴇᴍᴏᴛᴇ ɪɴᴛᴏ ғʀᴇᴇ ᴜsᴇʀ!**")
        return

    user_id = args[1]

    try:
        user = await bot.get_entity(uint(user_id))
        user_id = user.id
    except:
        await event.respond(f"**⚠️ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ:** ɴᴇᴠᴇʀ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴘʀᴇᴠɪᴏᴜsʟʏ!")
        return

    await db.add_premium_user(user_id)
    await event.reply(
        f"**ᴜsᴇʀ** `{user_id}` sᴜᴄᴄᴇssғᴜʟʟʏ **ᴅᴇᴍᴏᴛᴇᴅ**! 🚫"
    )

    try:
        udb = await db.get_user(user_id)
        exp = to_small_caps(udb.validity.strftime('%d-%m-%Y %I:%M:%S %p')) if getattr(udb, 'validity', None) else '🚫'
        text = (
            f"**⚠️ ɪᴍᴘᴏʀᴛᴀɴᴛ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ**"
            f"\n\n**ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ʜᴀs ᴇxᴘɪʀᴇᴅ. 😔**"
            f"\n\n>✅ **ᴘʟᴀɴ ᴅᴇᴛᴀɪʟs: {to_small_caps(udb.membership)} ᴘʀᴇᴍɪᴜᴍ**"
            f"\n📅 **ᴇxᴘɪʀᴀᴛɪᴏɴ ᴅᴀᴛᴇ: {exp}**>"
            f"\n\n**ʀᴇɴᴇᴡ ɴᴏᴡ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ᴇɴᴊᴏʏɪɴɢ ᴜɴɪɴᴛᴇʀʀᴜᴘᴛᴇᴅ ᴀᴄᴄᴇss ᴛᴏ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs! 🚀**"
            f"\n\n>♻️ **ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʀᴇɴᴇᴡ: /{command.get('plans')}**>"
            f"\n\n**ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ʙᴇɪɴɢ ᴡɪᴛʜ ᴜs!**"
        )

        if config.default.support:
            support_channel = resolve_tg_link(config.default.support)
            text += f" **( @{support_channel} ) !**"

        await bot.send_message(
            user_id,
            text
        )
    except Exception as e:
        print(e)