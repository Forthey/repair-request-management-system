from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.utility.render_buttons import render_inline_buttons

from database.queries.applications import get_applications
from schemas.applications import Application, ApplicationFull

router = Router()

get_app_commands = {
    "get_all_apps": "Все заявки",
    "get_worker_apps": "Ваши заявки",
}

all_app_list_commands = {
    "next_all_app_chunk": "Далее",
    "prev_all_app_chunk": "Назад",
}

worker_app_list_commands = {
    "next_worker_app_chunk": "Далее",
    "prev_worker_app_chunk": "Назад",
}


@router.message(StateFilter(None), F.text.lower() == "просмотреть заявки")
async def get_apps(message: Message, state: FSMContext):
    await message.answer(
        "Выберите, какие заявки Вы хотите просмотреть",
        reply_markup=render_inline_buttons(get_app_commands, 1)
    )

    await state.update_data(offset=0)


def apps_to_str(apps: list[ApplicationFull]) -> str:
    result: str = ""
    if len(apps) == 0:
        return "Пусто"

    for app in apps:
        result += (f"id = {app.id}\n"
                   f"Заявка создана: {app.created_at.date()}\n"
                   f"Клиент: {app.client_name}\n"
                   f"Контакт:\n"
                   f"    id={app.contact_id}\n"
                   f"    {app.contact.surname if app.contact.surname is not None else ""} "
                   f"{app.contact.name if app.contact.name is not None else ""} "
                   f"{app.contact.patronymic if app.contact.patronymic is not None else ""}\n"                
                   f"    {app.contact.email if app.contact.email is not None else ""} "
                   f"{app.contact.phone1 if app.contact.phone1 is not None else ""} "
                   f"{app.contact.phone2 if app.contact.phone2 is not None else ""} "
                   f"{app.contact.phone3 if app.contact.phone3 is not None else ""}\n"
                   f"Станок: {app.machine if app.machine is not None else "Не указан"}\n"
                   f"Причины заявки: {"; ".join(list(map(lambda reason: reason.name, app.reasons)))}\n"
                   f"Адрес: {app.address if app.address is not None else "Не указан"}\n"
                   f"Примерная дата ремонта: {
                        app.est_repair_date.date() if app.est_repair_date is not None else "Не указана"
                   }\n"
                   f"Примерное время ремонта (в часах): {
                        app.est_repair_duration_hours if app.est_repair_duration_hours else "Не указано"
                   }\n"
                   f"Взято в работу: {"Да" if app.repairer_id is not None else "Нет"}\n\n")

    return result


@router.callback_query(F.data == "get_all_apps")
async def get_all_apps(query: CallbackQuery, state: FSMContext):
    offset = (await state.get_data()).get("all_app_offset", 0)
    await state.update_data(all_app_offset=offset)

    apps: list[ApplicationFull] = await get_applications(offset, 1)

    await query.message.edit_text(
        apps_to_str(apps),
        reply_markup=render_inline_buttons(all_app_list_commands, 3)
    )


@router.callback_query(F.data == "next_all_app_chunk")
async def get_all_apps_offset_next(query: CallbackQuery, state: FSMContext):
    offset = (await state.get_data()).get("all_app_offset", 0)
    await state.update_data(all_app_offset=offset + 1)
    await get_all_apps(query, state)


@router.callback_query(F.data == "prev_all_app_chunk")
async def get_all_apps_offset_prev(query: CallbackQuery, state: FSMContext):
    offset = (await state.get_data()).get("all_app_offset", 0)
    await state.update_data(all_app_offset=max(0, offset - 1))
    await get_all_apps(query, state)


@router.callback_query(F.data == "get_worker_apps")
@router.callback_query(Command("get_apps"))
async def get_all_apps_from_worker(query: CallbackQuery, state: FSMContext):
    offset = (await state.get_data()).get("worker_app_offset", 0)
    await state.update_data(worker_app_offset=offset)

    apps: list[ApplicationFull] = await get_applications(offset, 1, worker_id=query.from_user.id)

    await query.message.edit_text(
        apps_to_str(apps),
        reply_markup=render_inline_buttons(worker_app_list_commands, 3)
    )


@router.callback_query(F.data == "next_worker_app_chunk")
async def get_worker_apps_offset_next(query: CallbackQuery, state: FSMContext):
    offset = (await state.get_data()).get("worker_app_offset", 0)
    await state.update_data(worker_app_offset=offset + 5)
    await get_all_apps_from_worker(query, state)


@router.callback_query(F.data == "prev_worker_app_chunk")
async def get_worker_apps_offset_prev(query: CallbackQuery, state: FSMContext):
    offset = (await state.get_data()).get("worker_app_offset", 0)
    await state.update_data(worker_app_offset=max(0, offset - 5))
    await get_all_apps_from_worker(query, state)
