from functools import wraps

from aiogram.filters import BaseFilter
from aiogram.types import Message

from redis_db.workers import check_common_access


class AuthFilter(BaseFilter):  # [1]
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        if not await check_common_access(message.from_user.id):
            await message.answer(
                text=f"У вас нет доступа для использования этого бота\n"
                     f"Если вы считаете, что это ошибка - обратитесь к администратору"
            )
            return False
        return True
