from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.routers.admin.admin_filter import AdminFilter

from bot.utility.get_id_by_username import get_user_id

router = Router()


class CommandFilter(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        args = message.text.split(" ")

        return len(args) > 0 and args[0] == "/id"


@router.message(CommandFilter(), AdminFilter())
async def get_id_from_username(message: Message):
    args = message.text.split(" ")
    if len(args) != 2:
        await message.answer("Формат комманды: /id username")
        return

    user_id = await get_user_id(args[1])
    if user_id is None:
        await message.answer("Такого юзера не существует")
        return
    await message.answer(f"{user_id}")
