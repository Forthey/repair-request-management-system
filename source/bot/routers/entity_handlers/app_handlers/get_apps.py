from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.utility.entities_to_str.app_to_str import app_to_str
from bot.utility.render_buttons import render_inline_buttons

from database.queries.applications import get_applications
from schemas.applications import ApplicationWithReasons

router = Router()


get_app_commands = {
    "get_all_apps": "Все заявки",
    "get_worker_apps": "Ваши заявки",
}

app_list_commands = {
    "next_app_chunk": "Далее",
    "prev_app_chunk": "Назад",
}


@router.message(StateFilter(None), F.text.lower() == "просмотреть заявки")
@router.message(Command("get_apps"))
async def get_apps(message: Message, state: FSMContext):
    await state.update_data(app_list_offset=0)
    apps: list[ApplicationWithReasons] = await get_applications(0, 3, worker_id=message.from_user.id)

    await message.answer(
        apps_to_str(apps),
        reply_markup=render_inline_buttons(app_list_commands, 3)
    )


def apps_to_str(apps: list[ApplicationWithReasons]) -> str:
    result: str = ""
    if len(apps) == 0:
        return "Пусто"

    for app in apps:
        result += app_to_str(app)

    return result


async def get_all_apps_from_worker(message: Message, state: FSMContext):
    offset = (await state.get_data()).get("app_list_offset", 0)

    apps: list[ApplicationWithReasons] = await get_applications(offset, 3, worker_id=message.from_user.id)

    if len(apps) == 0:
        return False

    await message.edit_text(
        apps_to_str(apps),
        reply_markup=render_inline_buttons(app_list_commands, 3)
    )

    return True


@router.callback_query(F.data == "next_app_chunk")
async def get_worker_apps_offset_next(query: CallbackQuery, state: FSMContext):
    offset = (await state.get_data()).get("app_list_offset", 0)
    await state.update_data(app_list_offset=offset + 3)
    if not await get_all_apps_from_worker(query.message, state):
        await state.update_data(app_list_offset=offset)


@router.callback_query(F.data == "prev_app_chunk")
async def get_worker_apps_offset_prev(query: CallbackQuery, state: FSMContext):
    offset = (await state.get_data()).get("app_list_offset", 0)
    if offset == 0:
        return
    await state.update_data(app_list_offset=max(0, offset - 3))
    await get_all_apps_from_worker(query.message, state)
