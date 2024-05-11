from aiogram import Router
from aiogram.types import Message

from config import settings


router = Router()


@router.message()
async def response_error(message: Message):
    await message.answer(
        text=f"Сущности \"{message.text.split(" ")[1]}\" не существует\n"
             f"Список доступных сущностей можно получить, написав @{settings.BOT_USERNAME}"
    )
