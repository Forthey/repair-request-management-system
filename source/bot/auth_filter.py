from functools import wraps

from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.cache_data import workers_id, fetch_workers


class AuthFilter(BaseFilter):  # [1]
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        if message.from_user.id not in workers_id:
            await message.answer(
                text=f"У вас нет доступа для использования этого бота\n"
                     f"Если вы считаете, что это ошибка - обратитесь к администратору"
            )
            return False
        return True
