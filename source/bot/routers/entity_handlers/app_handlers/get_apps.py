from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.routers.lister import create_lister
from bot.states.application import ApplicationListsState
from bot.utility.entities_to_str.app_to_str import app_to_str
from bot.utility.render_buttons import render_inline_buttons, render_keyboard_buttons

from database.queries.applications import get_applications, count_worker_applications, count_applications
from schemas.applications import ApplicationWithReasons

router = Router()

commands = [
    "Отмена"
]


def apps_to_str(apps: list[ApplicationWithReasons]) -> str:
    result: str = ""
    if len(apps) == 0:
        return "Пусто"

    for app in apps:
        result += app_to_str(app)
        result += "\n\n"

    return result


@router.message(StateFilter(None), F.text == "Просмотреть свои заявки")
@router.message(StateFilter(None), Command("get_apps"))
async def get_apps(message: Message, state: FSMContext):
    await message.answer(
        "Список ваших заявок",
        reply_markup=render_keyboard_buttons(commands, 1)
    )
    lister = await create_lister(
        get_applications, count_applications, apps_to_str,
        message, state,
        worker_id=message.from_user.id)


@router.message(StateFilter(None), F.text == "Просмотреть все заявки")
async def get_all_apps(message: Message, state: FSMContext):
    await message.answer(
        "Список заявок",
        reply_markup=render_keyboard_buttons(commands, 1)
    )
    lister = await create_lister(
        get_applications, count_applications, apps_to_str,
        message, state
    )
