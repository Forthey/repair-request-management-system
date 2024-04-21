from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.types import Message

from bot.routers.new_handlers.target_filter import TargetFilter
from bot.target_names import app_reason_strings
from database.queries.other import add_app_reason


# Router
router = Router()
router.message.filter(
    TargetFilter(app_reason_strings)
)


# Message handler
@router.message()
async def parseNewRequest(message: Message):
    new_reason = " ".join(message.text.split()[2:])
    reason = await add_app_reason(new_reason)
    if reason is not None:
        await message.answer(
            text=f"Добавлена причина заявки: {reason}"
        )
    else:
        await message.answer(
            text=f"Причина заявки {new_reason} уже существует"
        )
