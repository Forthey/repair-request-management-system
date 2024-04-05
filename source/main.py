import asyncio
import logging
from asyncio import WindowsSelectorEventLoopPolicy

from aiogram import Bot, Dispatcher

from bot.routers import base_handlers, add_worker_handlers
from config import settings

# Enable logging
logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher()

    dp.include_routers(add_worker_handlers.router, base_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    asyncio.run(main())
