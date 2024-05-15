from aiogram import Router
from aiogram.types import Message

from bot.routers.new_handlers.target_filter import TargetFilter
from bot.target_names import all_entity_strings
from database.queries.other import add_company_activity


# Router
router = Router()
router.message.filter(
    TargetFilter(all_entity_strings["company_activity_strings"])
)


# Message handler
@router.message()
async def parseNewRequest(message: Message):
    new_activity = " ".join(message.text.split()[2:])
    activity = await add_company_activity(new_activity)
    if activity is not None:
        await message.answer(
            text=f"Добавлена деятельность компании: {activity}"
        )
    else:
        await message.answer(
            text=f"Деятельность компании {new_activity} уже существует"
        )
