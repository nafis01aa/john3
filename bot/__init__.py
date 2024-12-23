import os
os.system('cls|clear')

import re
import ast
import asyncio
import telethon
from time import time
from contextlib import suppress
from telethon import TelegramClient
from configparser import ConfigParser
from datetime import datetime, timedelta
from telethon.sessions import StringSession
from dateutil.relativedelta import relativedelta

from logging import (
    getLogger,
    FileHandler,
    StreamHandler,
    INFO,
    ERROR,
    basicConfig
)

telethon.extensions.markdown.DEFAULT_DELIMITERS['>'] = telethon.types.MessageEntityBlockquote

getLogger("motor").setLevel(ERROR)
getLogger("pymongo").setLevel(ERROR)
getLogger("telethon").setLevel(ERROR)

class ConfigSection:
    def __init__(self, section):
        for key, value in section.items():
            with suppress(Exception):
                value = ast.literal_eval(value)
            setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

class Config:
    def __init__(self, filename):
        self.config = ConfigParser()
        self.config.optionxform = str
        self.config.read(filename)

        for section in self.config.sections():
            setattr(self, section, ConfigSection(dict(self.config[section])))

    def __contains__(self, section):
        return section in self.config.sections()

    def _parse_validity(self, validity_string):
        units = {
            "second": "seconds",
            "seconds": "seconds",
            "minute": "minutes",
            "minutes": "minutes",
            "hour": "hours",
            "hours": "hours",
            "day": "days",
            "days": "days",
            "week": "weeks",
            "weeks": "weeks",
            "month": "months",
            "months": "months",
            "year": "years",
            "years": "years",
        }

        match = re.match(r"(\d+)\s*(\w+)", validity_string.strip(), re.IGNORECASE)

        if not match:
            return None

        value, unit = match.groups()
        value = int(value)
        unit = units.get(unit.lower())

        if not unit:
            return None

        if unit in ["seconds", "minutes", "hours", "days", "weeks"]:
            return datetime.now() + timedelta(**{unit: value})
        elif unit in ["months", "years"]:
            return datetime.now() + relativedelta(**{unit: value})

        return None

    def _parse_plan(self, plan_key):
        plan_dict = {}
        description_key = f"{plan_key}_description"

        if description_key not in self.plans:
            return plan_dict

        raw_description = getattr(self.plans, description_key)
        description = raw_description.strip().strip('"').replace("\\n", "\n")
        lines = description.split("\n")

        for line in lines:
            if "Mass content" in line:
                match = re.search(r"\(max (\d+)\)|unlimited", line.strip(), re.IGNORECASE)
                if match:
                    plan_dict["mass_content_downloader"] = match.group(1) or "unlimited"
            elif "account login" in line:
                match = re.match(r"•\s*(\d+)\saccount login", line, re.IGNORECASE)
                if match:
                    plan_dict["account_login"] = int(match.group(1))
            elif "Up to" in line:
                match = re.search(r"Up to (\d+ GB)", line, re.IGNORECASE)
                if match:
                    plan_dict["content_limit"] = match.group(1)
            elif "Premium support" in line:
                plan_dict["premium_support"] = "✅" in line
            elif "Private chat" in line:
                plan_dict["private_chat_support"] = "✅" in line
            elif "Private inbox" in line:
                plan_dict["private_inbox_support"] = "✅" in line
            elif "Validity" in line:
                match = re.search(r"Validity\s+(.+)", line, re.IGNORECASE)
                if match:
                    validity_value = self._parse_validity(match.group(1))
                    plan_dict["validity"] = validity_value
                    plan_dict["validity_str"] = match.group(1)

        return plan_dict

    def get_plans_as_dict(self):
        plans = {}
        for plan_data in self.get_data('plan', _description="_description"):
            plan_number = plan_data['key']
            plans[plan_number] = self._parse_plan(plan_number)
        return plans

    def get_data(self, prefix, **kwargs):
        suffix = kwargs.get("_description", "_description")
        result = []

        for section in self.config.sections():
            for key, value in self.config[section].items():
                if key.startswith(prefix) and not key.endswith(suffix):
                    related_key = f"{key}{suffix}"
                    description = self.config[section].get(related_key, "No description available")
                    result.append({'key': key, 'keyvalue': ast.literal_eval(value), "desc": description})

        return tuple(result)

start_time = time()
states_manager = {}
log_file = "log.txt"
root_dir = os.getcwd()
logger = getLogger(__name__)
config = Config('config.ini')

basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[FileHandler(log_file), StreamHandler()],
    level=INFO
)

REQUIRED_CATEGORIES = [
    "telegram",
    "mongodb",
    "owner"
]

for req_key in REQUIRED_CATEGORIES:
    keyable = getattr(config, req_key, None)
    for key in vars(keyable) if keyable else []:
        if key not in getattr(config, req_key):
            logger.error(f"\"{key}\" not found in config")
            quit(1)
        else:
            if not getattr(getattr(config, req_key), key):
                logger.error(f"\"{key}\" must required in \"{req_key}\" on config")
                quit(1)

logger.info("Initializing Content Saver Bot...")

bot = TelegramClient(
    "contentbot",
    config.telegram.api,
    config.telegram.hash
).start(bot_token=config.telegram.token)

me = bot.loop.run_until_complete(bot.get_me())

logger.info(f"@{me.username} Content Bot Initialized!")

loop = bot.loop
bot_id = me.id
bot_username = me.username

owner = owner_info = bot.loop.run_until_complete(bot.get_entity(config.owner.id))
owner_username = owner_ua = owner_info.username

if config.default.string:
    user = TelegramClient(
        StringSession(config.default.string),
        config.telegram.api,
        config.telegram.hash,
        sequential_updates=False,
        receive_updates=False
    )
    bot.loop.run_until_complete(user.connect())
else:
    user = None