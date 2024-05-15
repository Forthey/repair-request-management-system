from aiogram import Router
from aiogram.types import Message

from bot.routers.new_handlers.target_filter import TargetFilter
from bot.target_names import all_entity_strings
from database.queries.clients import add_client
from schemas.clients import ClientAdd

# Router
router = Router()
router.message.filter(
    TargetFilter(all_entity_strings["client_strings"])
)


# Message handler
@router.message()
async def parseNewRequest(message: Message):
    new_client = " ".join(message.text.split()[2:])
    client = await add_client(ClientAdd(name=new_client))
    if client:
        await message.answer(
            text=f"Добавлен клиент: {client}"
        )
    else:
        await message.answer(
            text=f"Клиент {new_client} уже существует"
        )
