from aiogram.filters import BaseFilter
from aiogram.types import Message

from redis_db.workers import check_admin_rights


class AdminFilter(BaseFilter):  # [1]
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        return await check_admin_rights(message.from_user.id)
