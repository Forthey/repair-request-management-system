from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message


# Nester routers
from bot.routers.admin.worker_handlers import add_worker
# Button from list renderer
from bot.utility.render_buttons import render_keyboard_buttons
from bot.commands import worker_commands

router = Router()


@router.message(StateFilter(None), F.text.lower() == "работники")
async def print_help(message: Message):
    await message.answer(
        text="Выберите действие",
        reply_markup=render_keyboard_buttons(worker_commands, 2)
    )


router.include_routers(
    add_worker.router,
)