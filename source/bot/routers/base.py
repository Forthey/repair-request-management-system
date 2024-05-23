from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.utility.render_buttons import render_keyboard_buttons

from bot.auth_filter import AuthFilter

# Nested routers
from bot.routers.utility_commands import get_id_from_username
from bot.routers.new_handlers import new_base
from bot.routers.seacrh_handlers import search_base
from bot.routers.help_handlers import help_base
from bot.routers.entity_handlers.app_handlers import app_base
from bot.routers.entity_handlers.machine_handlers import machines_base
from bot.routers.entity_handlers.client_handlers import client_base
from bot.routers.entity_handlers.contact_handlers import contact_base
from bot.routers.entity_handlers.address_handlers import address_base

from bot.routers.admin import admin_base
# Commands
from bot.commands import base_commands, admin_base_commands


router = Router()
router.message.filter(
    AuthFilter()
)


@router.message(Command("start"))
@router.message(StateFilter(None), F.text.lower() == "вывести подсказки")
async def print_help(message: Message):
    await message.answer(
        text="Выберите действие",
        reply_markup=render_keyboard_buttons(base_commands, 2)
    )


@router.message(F.text.lower() == "отмена")
async def cancel(message: Message, state: FSMContext):
    state_str = await state.get_state()

    if state_str is None:
        await state.set_data({})
        await message.answer(
            text="Выберите действие",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )
        return

    await state.clear()
    await message.answer(
        text="Отменено",
        reply_markup=render_keyboard_buttons(base_commands, 2)
    )


@router.message(F.text == "$skip")
async def print_help(message: Message):
    await message.answer("Сообщение проигнорировано")


router.include_routers(
    get_id_from_username.router,
    new_base.router,
    search_base.router,
    help_base.router,
    app_base.router,
    machines_base.router,
    client_base.router,
    contact_base.router,
    address_base.router,
    admin_base.router
)
