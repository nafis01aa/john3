import asyncio
import telethon
import threading
from telethon import types
from telethon.tl.custom.button import Button
from concurrent.futures import ThreadPoolExecutor

from bot import bot, config

class button:
    def __init__(self, inline=True):
        self.buttons = []
        self.header = []
        self.footer = []
        Button._is_inline = staticmethod(lambda b: inline)

    def __run(self, coro, future):
        loop = asyncio.new_event_loop()

        try:
            f = loop.run_until_complete(coro)
            future.set_result(f)
        except Exception as e:
            future.set_exception(e)

    def _await(self, coro):
        future = asyncio.Future()
        thread = threading.Thread(target=self.__run, args=(coro, future))
        thread.start()
        thread.join()
        result = future.result()
        del thread
        return result

    def inline(self, key, data=None, position=None):
        call = getattr(self, "buttons") if not position else getattr(self, "header") if "header" in position.lower() else getattr(self, "footer")
        call.append(Button.inline(key, data))
        return self

    def user_id(self, key, uid, position=None):
        call = getattr(self, "buttons") if not position else getattr(self, "header") if "header" in position.lower() else getattr(self, "footer")
        call.append(types.InputKeyboardButtonUserProfile(key, self._await(bot.get_input_entity(uid))))
        return self

    def url(self, key, url, position=None):
        call = getattr(self, "buttons") if not position else getattr(self, "header") if "header" in position.lower() else getattr(self, "footer")
        call.append(Button.url(key, url))
        return self

    def menu(self, *keys, position=None):
        for key in keys:
            call = getattr(self, "buttons") if not position else getattr(self, "header") if "header" in position.lower() else getattr(self, "footer")
            call.append(Button.text(key, resize=True))
        return self

    @staticmethod
    def remove():
        return Button.clear()

    @staticmethod
    def format(num, divisor):
        quotient = num // divisor
        remainder = [num % divisor] if num % divisor else []
        return [divisor] * quotient + remainder

    def build(self, rows=1, columns=None):
        if columns is None:
            columns = len(self.buttons) // rows * [rows]
            remainder = len(self.buttons) % rows

            if remainder:
                columns.append(remainder)

        def split_buttons(buttons, columns):
            index = 0
            keyboard = []
            for count in columns:
                row = buttons[index:index + count]
                keyboard.append(row)
                index += count
            return keyboard

        complete_buttons = self.header + self.buttons + self.footer
        keyboard = split_buttons(self.buttons, columns)
        complete_keyboard = [self.header] + keyboard + [self.footer]

        for i in complete_keyboard:
            if not i:
                complete_keyboard.remove(i)

        return complete_keyboard

    @classmethod
    def start(cls, *args, event=None, **kwargs):
        text = (
            f"ʜɪ👋, ɪ ᴀᴍ ꜱᴀᴠᴇ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ ʙᴏᴛ.\n\n"
            f"**• ꜰʀᴏᴍ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟꜱ**\n"
            f"- ꜱᴇɴᴅ ᴅɪʀᴇᴄᴛ ᴍᴇꜱꜱᴀɢᴇ/ᴠɪᴅᴇᴏ ʟɪɴᴋ ᴛᴏ ᴄʟᴏɴᴇ ɪᴛ ʜᴇʀᴇ.\n"
            f"ᴇxᴀᴍᴘʟᴇ- `https://t.me/bdbots/72`\n\n"
            f"🚨ɴᴏᴛᴇ:- ᴏᴜʀ ʙᴏᴛ ᴅᴏᴇꜱ ꜱᴜᴘᴘᴏʀᴛ\n"
            f"ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟ/ɢʀᴏᴜᴘ, ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴏɴʟʏ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ. ᴄʜᴇᴄᴋ ᴘʟᴀɴꜱ ʙʏ /ᴘʟᴀɴꜱ.\n\n"
            f"ʙᴏᴛ ʜᴀꜱ ᴀ ᴛɪᴍᴇ ʟɪᴍɪᴛ ᴏꜰ 30 ꜱᴇᴄ."
        )
        m = cls()
        m.user_id("Owner ✔️", config.owner.id)
        return text, m.build()