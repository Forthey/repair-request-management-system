from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message


# Nester routers
from bot.routers.entity_handlers.client_handlers import add_client, merge_clients
# Button from list renderer
from bot.utility.render_buttons import render_keyboard_buttons
from bot.commands import client_commands, admin_client_commands
from redis_db.workers import check_admin_rights

router = Router()


@router.message(StateFilter(None), F.text.lower() == "клиенты")
async def print_help(message: Message):
    available_commands: list[str] = client_commands
    if await check_admin_rights(message.from_user.id):
        available_commands = admin_client_commands + client_commands

    await message.answer(
        text="Выберите действие",
        reply_markup=render_keyboard_buttons(available_commands, 2)
    )


router.include_routers(
    add_client.router,
    merge_clients.router
)
