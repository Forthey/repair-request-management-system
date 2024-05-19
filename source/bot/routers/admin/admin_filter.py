from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.queries.workers import get_worker


class AdminFilter(BaseFilter):  # [1]
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        worker = await get_worker(message.from_user.id)
        return worker.access_right.lower() == "админ"
