from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from bot import bot, logger, config

class objecter:
    def __init__(self, dictionary={}):
        self.__dict__ = dict(dictionary)

class db_handle:
    def __init__(self, name, url):
        self.name = str(name)
        self.url = url
        self.connect()

    def connect(self):
        try:
            self.conn = AsyncIOMotorClient(self.url)
            self.db = self.conn[self.name]
            self.users = self.db.Users
        except Exception as e:
            logger.error(e, exc_info=True)
            exit(1)

    async def update_user(self, user_id):
        user_id = str(user_id)
        if not await self.users.find_one({"user_id": user_id}):
            await self.users.insert_one({
                "user_id": user_id,
                "membership": "free",
                "total_downloads": 0,
                "login_accounts": [],
                "total_downloads_limit": 10,
                "today_remaining_limit": 10,
                "last_download_date": datetime.now(),
                "total_purchased_stars": 0,
                "joined_at": datetime.now()
            })

    async def get_user(self, user_id):
        user_id = str(user_id)

        if document := await self.users.find_one({"user_id": user_id}):
            return objecter(document)
        return None

    async def add_premium_user(self, user_id, **kwargs):
        user_id = str(user_id)
        membership = kwargs.get('membership', 'free')
        total_downloads_limit = kwargs.get('total', 10)
        today_remaining_limit = kwargs.get('total', 10)
        validity = kwargs.get('validity', None)

        query = {
            "$set": {
                "membership": membership,
                "total_downloads_limit": total_downloads_limit,
                "today_remaining_limit": today_remaining_limit
            }
        }

        if validity:
            query["$set"]["validity"] = validity
        else:
            query["$unset"] = {
                "validity": "",
                "last_reminder": ""
            }

        if document := await self.users.find_one({"user_id": user_id}):
            await self.users.update_one(
                {"_id": document["_id"]},
                query,
                upsert=True
            )

    async def mark_download(self, user_id):
        user_id = str(user_id)

        if document := await self.users.find_one({"user_id": user_id}):
            if document['total_downloads_limit'] != 'unlimited':
                await self.users.update_one(
                    {"_id": document["_id"]},
                    {"$inc": {"today_remaining_limit": -1}}
                )

    async def add_new_login(self, user_id, **kwargs):
        name = kwargs.get('name')
        id = kwargs.get('id')
        string = kwargs.get('string')
        user_id = str(user_id)

        if document := await self.users.find_one({"user_id": user_id}):
            await self.users.update_one(
                {"_id": document["_id"]},
                {"$push": {
                    'login_accounts': {
                        'name': name,
                        'id': id,
                        'string': string,
                        'in_using': False
                    },
                }},
                upsert=True
            )

    async def remove_login(self, user_id, **kwargs):
        user_id = str(user_id)

        if document := await self.users.find_one({"user_id": user_id}):
            await self.users.update_one(
                {"_id": document["_id"]},
                {"$pull": {
                    "login_accounts": dict(kwargs)
                }}
            )

    async def mark_string(self, user_id, string, flag=True):
        user_id = str(user_id)

        if document := await self.users.find_one({"user_id": user_id}):
            try:
                await self.users.update_one(
                    {"_id": document["_id"], "login_accounts.string": string},
                    {"$set": {f"login_accounts.$.in_using": flag}},
                    upsert=False
                )
            except:
                pass

    async def is_string_running(self, user_id, string):
        user_id = str(user_id)

        if document := await self.users.find_one({"user_id": user_id}):
            sdict = next((d for d in document.get('login_accounts', []) if d['string'] == string), None)
            if sdict and sdict.get("in_using", False):
                return True
            return False

db = db_handle(
    config.mongodb.name if config.mongodb.name else 'TelegramContentSaver',
    config.mongodb.url
)