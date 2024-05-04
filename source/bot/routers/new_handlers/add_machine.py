from aiogram import Router
from aiogram.types import Message

from bot.routers.new_handlers.target_filter import TargetFilter
from bot.target_names import machine_strings
from database.queries.machines import add_machine


# Router
router = Router()
router.message.filter(
    TargetFilter(machine_strings)
)


# Message handler
@router.message()
async def parseNewRequest(message: Message):
    new_machine = " ".join(message.text.split()[2:])
    machine = await add_machine(new_machine)
    if not machine:
        await message.answer(
            text=f"Добавлен станок: {new_machine}"
        )
    else:
        await message.answer(
            text=f"Станок {new_machine} уже существует"
        )
