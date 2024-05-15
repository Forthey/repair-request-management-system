from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message


# Nester routers
from bot.routers.entity_handlers.app_handlers import add_app, get_apps, get_one_app, edit_app
# Button from list renderer
from bot.utility.render_buttons import render_keyboard_buttons
from bot.commands import app_commands

router = Router()


@router.message(StateFilter(None), F.text.lower() == "заявки")
async def print_help(message: Message):
    await message.answer(
        text="Выберите действие",
        reply_markup=render_keyboard_buttons(app_commands, 2)
    )


router.include_routers(
    get_one_app.router,
    add_app.router,
    edit_app.router,
    get_apps.router
)
