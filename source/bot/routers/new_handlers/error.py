from aiogram import Router
from aiogram.types import Message

router = Router()


router.message()
async def response_error(message: Message):
    await message.answer(
        text=f"Сущности \"{message.text.split(" ")[1]}\" не существует"
    )
