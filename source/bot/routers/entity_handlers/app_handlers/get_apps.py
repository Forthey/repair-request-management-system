from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.states.application import ApplicationListsState
from bot.utility.entities_to_str.app_to_str import app_to_str
from bot.utility.render_buttons import render_inline_buttons, render_keyboard_buttons

from database.queries.applications import get_applications, count_worker_applications
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

commands = [
    "Отмена"
]


@router.message(StateFilter(None), F.text.lower() == "просмотреть заявки")
@router.message(StateFilter(None), Command("get_apps"))
async def get_apps(message: Message, state: FSMContext):
    apps_number = await count_worker_applications(message.from_user.id)

    chunk_size = 3
    await state.update_data(max_offset=apps_number)
    await state.update_data(offset=0)
    await state.update_data(chunk_size=chunk_size)

    apps: list[ApplicationWithReasons] = await get_applications(0, chunk_size, worker_id=message.from_user.id)

    await message.answer(
        "Список заявок",
        reply_markup=render_keyboard_buttons(commands, 1)
    )
    await message.answer(
        apps_to_str(apps),
        reply_markup=render_inline_buttons(app_list_commands, 3)
    )
    await state.set_state(ApplicationListsState.list_by_worker)


def apps_to_str(apps: list[ApplicationWithReasons]) -> str:
    result: str = ""
    if len(apps) == 0:
        return "Пусто"

    for app in apps:
        result += app_to_str(app)
        result += "\n\n"

    return result


async def get_all_apps_from_worker(message: Message, state: FSMContext):
    data = await state.get_data()
    offset = data.get("offset", 0)
    chunk_size = data.get("chunk_size", 3)

    worker_id = data.get("worker_id", message.from_user.id)

    apps: list[ApplicationWithReasons] = await get_applications(offset, chunk_size, worker_id=worker_id)

    await message.edit_text(
        apps_to_str(apps),
        reply_markup=render_inline_buttons(app_list_commands, 3)
    )

    return True


@router.callback_query(StateFilter(ApplicationListsState.list_by_worker), F.data == "next_app_chunk")
async def get_worker_apps_offset_next(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    max_offset = data.get("max_offset", 0)
    offset = data.get("offset", 0)
    chunk_size = data.get("chunk_size", 3)

    if offset >= max_offset - chunk_size:
        await query.answer("Это последняя страница")
        return

    await state.update_data(offset=offset + chunk_size)
    await get_all_apps_from_worker(query.message, state)


@router.callback_query(StateFilter(ApplicationListsState.list_by_worker), F.data == "prev_app_chunk")
async def get_worker_apps_offset_prev(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    offset = data.get("offset", 0)
    chunk_size = data.get("chunk_size", 3)

    if offset <= 0:
        await query.answer("Это первая страница")
        return 
    await state.update_data(offset=max(0, offset - chunk_size))
    await get_all_apps_from_worker(query.message, state)
