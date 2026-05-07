import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

from sqlalchemy.sql.coercions import expect

load_dotenv()
api_key = os.getenv("API_KEY")
PROXY_URL = 'https://t.me/proxy?server=127.0.0.1&port=1080&secret=dd42392b95201fba78d3ee942eb63dce0b'
dp = Dispatcher()


async def main():
    try:
        bot = Bot(token=api_key, default=DefaultBotProperties(parse_mode=ParseMode.HTML), proxy=PROXY_URL)
        await dp.start_polling(bot)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
