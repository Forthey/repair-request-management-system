from aiogram import Router, F
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message

from bot.routers.new_handlers.target_filter import TargetFilter
from bot.target_names import company_position_strings
from database.queries.other import add_company_position


# Router
router = Router()
router.message.filter(
    TargetFilter(company_position_strings)
)


# Message handler
@router.message()
async def parseNewRequest(message: Message):
    new_position = " ".join(message.text.split()[2:])
    position = await add_company_position(new_position)
    if position is not None:
        await message.answer(
            text=f"Добавлена должность: {position}"
        )
    else:
        await message.answer(
            text=f"Должность {new_position} уже существует"
        )
