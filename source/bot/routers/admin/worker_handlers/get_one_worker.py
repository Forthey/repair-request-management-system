from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.routers.entity_handlers.app_handlers.get_apps import apps_to_str
from bot.states.worker import OneWorkerState
from bot.utility.entities_to_str.worker_to_str import worker_to_str
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
from database.queries.applications import get_applications, count_worker_applications
from database.queries.workers import get_worker, update_worker
from redis_db.workers import reload_worker
from schemas.applications import ApplicationWithReasons
from schemas.workers import Worker


router = Router()


commands = [
    "Отмена"
]


buttons = {
    "fire_worker": "Сделать неактивным",
    "restore_worker": "Восстановить",
    "promote_worker": "Повысить до админа",
    "demote_worker": "Понизить до работника",
    "get_apps_from_worker": "Отобразить заявки",
    "choose_another_worker": "Выбрать другого"
}

app_list_buttons = {
    "next_app_chunk": "Далее",
    "prev_app_chunk": "Назад",
    "go_back_to_worker": "Вернуться к работнику"
}


@router.message(StateFilter(None), F.text.lower() == "выбрать работника")
async def get_one_worker(message: Message, state: FSMContext):
    await message.answer(
        "Введите id работника в телеграме",
        reply_markup=render_keyboard_buttons(commands, 1)
    )

    await state.set_state(OneWorkerState.choosing_worker_id)


@router.message(StateFilter(OneWorkerState.choosing_worker_id), F.text)
async def get_worker_by_id(message: Message, state: FSMContext):
    worker_id: int
    try:
        worker_id = int(message.text)
    except ValueError:
        await message.answer("Указан не id")
        return

    worker = await get_worker(worker_id, True)
    if worker is None:
        await message.answer(f"Работника с id {worker_id} не существует")
        return

    await state.update_data(worker_id=worker.telegram_id)

    active_buttons: dict[str, str] = dict()

    if worker.active:
        active_buttons["fire_worker"] = buttons["fire_worker"]
    else:
        active_buttons["restore_worker"] = buttons["restore_worker"]
    if worker.access_right == "Работник":
        active_buttons["promote_worker"] = buttons["promote_worker"]
    else:
        active_buttons["demote_worker"] = buttons["demote_worker"]
    active_buttons["get_apps_from_worker"] = buttons["get_apps_from_worker"]
    active_buttons["choose_another_worker"] = buttons["choose_another_worker"]

    await message.answer(
        worker_to_str(worker),
        reply_markup=render_inline_buttons(active_buttons, 1)
    )
    await state.set_state(OneWorkerState.choosing_worker_confirmation)


@router.callback_query(StateFilter(OneWorkerState.choosing_worker_confirmation), F.data.in_(buttons))
async def manage_worker(query: CallbackQuery, state: FSMContext):
    if query.data == "fire_worker":
        await do_fire_worker(query, state)
    elif query.data == "restore_worker":
        await do_restore_worker(query, state)
    elif query.data == "promote_worker":
        await do_promote_worker(query, state)
    elif query.data == "demote_worker":
        await do_demote_worker(query, state)
    elif query.data == "get_apps_from_worker":
        await get_apps_from_worker(query, state)
    elif query.data == "choose_another_worker":
        await query.message.answer(
            "Введите id работника в телеграме",
            reply_markup=render_keyboard_buttons(commands, 1)
        )
        await state.set_state(OneWorkerState.choosing_worker_id)


async def refresh_worker(message: Message, worker: Worker):
    active_buttons: dict[str, str] = dict()
    if worker.active:
        active_buttons["fire_worker"] = buttons["fire_worker"]
    else:
        active_buttons["restore_worker"] = buttons["restore_worker"]
    if worker.access_right == "Работник":
        active_buttons["promote_worker"] = buttons["promote_worker"]
    else:
        active_buttons["demote_worker"] = buttons["demote_worker"]
    active_buttons["get_apps_from_worker"] = buttons["get_apps_from_worker"]
    active_buttons["choose_another_worker"] = buttons["choose_another_worker"]

    await message.edit_text(
        worker_to_str(worker),
        reply_markup=render_inline_buttons(active_buttons, 1)
    )


async def do_update_worker_state(query: CallbackQuery, state: FSMContext, **fields):
    worker_id = (await state.get_data()).get("worker_id")
    if worker_id is None:
        await query.answer("Что-то пошло не так...")
        return
    worker = await update_worker(worker_id, **fields)
    if worker is None:
        await query.answer("Что-то пошло не так...")
        return

    await refresh_worker(query.message, worker)

    await reload_worker(worker.telegram_id)


async def do_fire_worker(query: CallbackQuery, state: FSMContext):
    await do_update_worker_state(query, state, active=False)
    await query.answer("Работник теперь неактивен")


async def do_restore_worker(query: CallbackQuery, state: FSMContext):
    await do_update_worker_state(query, state, active=True)
    await query.answer("Работник восстановлен")


async def do_promote_worker(query: CallbackQuery, state: FSMContext):
    await do_update_worker_state(query, state, access_right="Админ")
    await query.answer("Работник теперь Админ")


async def do_demote_worker(query: CallbackQuery, state: FSMContext):
    await do_update_worker_state(query, state, access_right="Работник")
    await query.answer("Работник теперь... Работник!")


async def get_apps_from_worker(query: CallbackQuery, state: FSMContext):
    worker_id = (await state.get_data()).get("worker_id")
    if worker_id is None:
        await query.answer("Что-то пошло не так...")
        return
    apps_number = await count_worker_applications(worker_id)

    chunk_size = 3
    await state.update_data(max_offset=apps_number)
    await state.update_data(offset=0)
    await state.update_data(chunk_size=chunk_size)
    await state.set_state(OneWorkerState.listing_worker_apps)
    await get_all_apps_from_worker(query.message, state)


async def get_all_apps_from_worker(message: Message, state: FSMContext):
    data = await state.get_data()
    offset = data.get("offset", 0)
    chunk_size = data.get("chunk_size", 3)

    worker_id = data.get("worker_id", message.from_user.id)

    apps: list[ApplicationWithReasons] = await get_applications(offset, chunk_size, worker_id=worker_id)

    await message.edit_text(
        apps_to_str(apps),
        reply_markup=render_inline_buttons(app_list_buttons, 2)
    )
    return True


@router.callback_query(StateFilter(OneWorkerState.listing_worker_apps), F.data == "next_app_chunk")
async def get_worker_apps_offset_next(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    max_offset = data.get("max_offset", 0)
    offset = data.get("offset", 0)
    chunk_size = data.get("chunk_size", 3)

    if offset > max_offset - chunk_size:
        await query.answer("Это последняя страница")
        return

    await state.update_data(offset=offset + chunk_size)
    await get_all_apps_from_worker(query.message, state)


@router.callback_query(StateFilter(OneWorkerState.listing_worker_apps), F.data == "prev_app_chunk")
async def get_worker_apps_offset_prev(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    offset = data.get("offset", 0)
    chunk_size = data.get("chunk_size", 3)

    if offset <= 0:
        await query.answer("Это первая страница")
        return
    await state.update_data(offset=max(0, offset - chunk_size))
    await get_all_apps_from_worker(query.message, state)


@router.callback_query(StateFilter(OneWorkerState.listing_worker_apps), F.data == "go_back_to_worker")
async def go_back_to_worker(query: CallbackQuery, state: FSMContext):
    worker_id = (await state.get_data()).get("worker_id")
    if worker_id is None:
        await query.answer("Что-то пошло не так...")
        return
    worker = await get_worker(worker_id, True)
    if worker is None:
        await query.answer("Что-то пошло не так...")
        return
    await refresh_worker(query.message, worker)
    await state.set_data({"worker_id": worker.telegram_id})
    await state.set_state(OneWorkerState.choosing_worker_confirmation)
