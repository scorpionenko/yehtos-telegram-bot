import asyncio
from aiogram import Bot, Dispatcher
from bot.config import TOKEN
from bot.handlers import router
from bot.db import connect_db, init_tables

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(router)

async def main():
    await connect_db()      #  підключення до БД
    await init_tables()     #  створення таблиць

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())