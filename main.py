# точка входа, запуск бота
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from db import init_db
from handlers import admin, foreman, worker

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

async def main():
    await init_db()
    dp.include_router(admin.router)
    dp.include_router(foreman.router)
    dp.include_router(worker.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
