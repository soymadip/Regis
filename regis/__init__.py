import logging
import logging.config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from regis.database.ia_filterdb import Media
from regis.database.users_chats_db import db
from regis.info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR
from regis.utils import temp

class Bot(Client):

    def __init__(self):
        super().__init__(
            session_name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes() 
        btn = [
        [
            InlineKeyboardButton('⚡️ ℂ𝕀ℕ𝔼𝕄𝔸 ℍ𝕌𝔹 ⚡️', url=f'https://t.me/cinemahub02')
        ]
        ]
        #m = await self.send_message(
           # chat_id=-1001308633613,
         #   text="🧭🧭 GROUP OPENED 🧭🧭\n\n🤖 Bot started.\n\n🪶 Group unlocked.\n\n✅ Requests are allowed, Let's start.", 
         #   reply_markup=InlineKeyboardMarkup(btn)
       # )
        #await m.pin()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.username} with Pyrogram v{__version__} (Layer {layer}) started by {me.first_name}.")
        logging.info(LOG_STR)

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")


app = Bot()


def main():
    app.run()


if __name__ == "__main__":
    main()
