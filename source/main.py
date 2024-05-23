import asyncio
import logging
# from asyncio import WindowsSelectorEventLoopPolicy

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from bot.routers import base
from config import settings
from redis_db.workers import load_workers

# Enable logging
logging.basicConfig(level=logging.INFO)


async def main():
    await load_workers()

    bot = Bot(token=settings.TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        base.router,
    )

    bot_commands = [
        BotCommand(command="/help", description="Вывести подсказки"),
        BotCommand(command="/new", description="Добавление новой сущности"),
        BotCommand(command="/get_apps", description="Просмотреть заявки"),
    ]
    await bot.set_my_commands(bot_commands)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    asyncio.run(main())
