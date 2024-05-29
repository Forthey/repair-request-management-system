from aiogram import Router
from aiogram.types import Message

from config import settings


router = Router()


@router.message()
async def response_error(message: Message):
    args = message.text.split(" ")
    if len(args) < 3:
        await message.answer(
            text="Недостаточно параметров для вызова new\n"
                 "Проверьте, что формат ввода верный\n"
                 "Например: new должность менеджер\n"
        )
        return
    await message.answer(
        text=f"Сущности \"{message.text.split(" ")[1]}\" не существует или её невозможно добавить через /new\n"
             f"Список доступных сущностей можно получить, написав {settings.BOT_USERNAME}"
    )
