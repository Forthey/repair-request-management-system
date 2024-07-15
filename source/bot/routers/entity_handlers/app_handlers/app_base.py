from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message


# Nester routers
from bot.routers.entity_handlers.app_handlers import add_app, get_apps, get_one_app, edit_app, app_auto_fields_add
# Button from list renderer
from bot.utility.render_buttons import render_keyboard_buttons
from bot.commands import app_commands, admin_app_commands
from redis_db.workers import check_admin_rights

router = Router()


@router.message(StateFilter(None), F.text.lower() == "заявки")
async def print_help(message: Message):
    available_commands: list[str] = app_commands
    if await check_admin_rights(message.from_user.id):
        available_commands = admin_app_commands + app_commands

    await message.answer(
        text="Выберите действие",
        reply_markup=render_keyboard_buttons(available_commands, 2)
    )


router.include_routers(
    get_one_app.router,
    add_app.router,
    edit_app.router,
    app_auto_fields_add.router,
    get_apps.router
)
