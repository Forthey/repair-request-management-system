from aiogram import Router
from aiogram.types import Message

from bot.routers.new_handlers.target_filter import TargetFilter
from bot.target_names import all_entity_strings
from database.queries.other import add_close_reason

# Router
router = Router()
router.message.filter(
    TargetFilter(all_entity_strings["close_reason_strings"])
)


# Message handler
@router.message()
async def parseNewRequest(message: Message):
    new_reason = " ".join(message.text.split()[2:])
    reason = await add_close_reason(new_reason)
    if reason is not None:
        await message.answer(
            text=f"Добавлена причина закрытия заявки: {reason}"
        )
    else:
        await message.answer(
            text=f"Причина закрытия заявки {new_reason} уже существует"
        )
