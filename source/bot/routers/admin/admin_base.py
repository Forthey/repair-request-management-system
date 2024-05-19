from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.routers.admin.admin_filter import AdminFilter
from bot.routers.admin.worker_handlers import workers_base
from bot.commands import admin_base_commands
from bot.utility.render_buttons import render_keyboard_buttons

router = Router()
router.message.filter(AdminFilter())

router.include_routers(
    workers_base.router
)


@router.message(Command("admin"))
async def print_admin_command(message: Message):
    await message.answer(
        "Выберите действие",
        reply_markup=render_keyboard_buttons([*admin_base_commands, "Отмена"], 2)
    )
