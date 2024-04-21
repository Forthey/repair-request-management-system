from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message


# Nester routers
from bot.routers.address_handlers import (
    add_address
)
# Button from list renderer
from bot.utility.render_buttons import render_keyboard_buttons
from bot.commands import address_commands

router = Router()


@router.message(StateFilter(None), F.text.lower() == "адреса")
async def print_help(message: Message):
    await message.answer(
        text="Выберите действие",
        reply_markup=render_keyboard_buttons(address_commands, 2)
    )


router.include_routers(
    add_address.router,
)
