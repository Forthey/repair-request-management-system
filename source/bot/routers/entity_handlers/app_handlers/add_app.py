import datetime
import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from pydantic import ValidationError

from bot.routers.entity_handlers.app_handlers.app_fields_parser import parse_app_client, parse_app_contact, \
    parse_app_reason, parse_app_machine, parse_app_address, parse_app_est_repair_date_and_duration

from bot.states.application import AddApplicationState, add_states_strings
from bot.commands import base_commands
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons

import database.queries.applications as db_apps
from database.queries.addresses import add_address, get_address
from database.queries.clients import add_client
from database.queries.machines import add_machine, get_machine
from schemas.addresses import AddressAdd
from schemas.applications import ApplicationAdd
from schemas.clients import ClientAdd

router = Router()

commands = [
    "Далее",
    "Назад",
    "Отмена"
]


@router.message(StateFilter(None), F.text.lower() == "добавить заявку")
async def add_app_begin(message: Message, state: FSMContext):
    await message.answer(
        text="Создание новой заявки",
        reply_markup=render_keyboard_buttons(commands, 2)
    )

    await message.answer(add_states_strings[AddApplicationState.choosing_app_client])
    await state.set_state(AddApplicationState.choosing_app_client)


@router.message(StateFilter(AddApplicationState.choosing_app_client), F.text)
async def choosing_app_client(message: Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Это первое поле")
        return

    if message.text != "Далее":
        if not await parse_app_client(message, state):
            return

    await state.set_state(AddApplicationState.choosing_app_contact)
    await message.answer(add_states_strings[AddApplicationState.choosing_app_contact])


@router.message(StateFilter(AddApplicationState.choosing_app_contact), F.text)
async def choosing_app_contact(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AddApplicationState.choosing_app_client)
        await message.answer(add_states_strings[AddApplicationState.choosing_app_client])
        return

    if message.text != "Далее":
        if not await parse_app_contact(message, state):
            return

    await state.set_state(AddApplicationState.choosing_app_reasons)
    await message.answer(add_states_strings[AddApplicationState.choosing_app_reasons])


@router.message(StateFilter(AddApplicationState.choosing_app_reasons), F.text)
async def choosing_app_reasons(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AddApplicationState.choosing_app_contact)
        await message.answer(add_states_strings[AddApplicationState.choosing_app_contact])
        return

    if message.text == "Далее":
        await state.set_state(AddApplicationState.choosing_app_machine)
        await message.answer(add_states_strings[AddApplicationState.choosing_app_machine])
        return

    if not await parse_app_reason(message, state):
        return


@router.message(StateFilter(AddApplicationState.choosing_app_machine), F.text)
async def choosing_app_machine(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AddApplicationState.choosing_app_reasons)
        await message.answer(add_states_strings[AddApplicationState.choosing_app_reasons])
        return

    if message.text != "Далее":
        if not await parse_app_machine(message, state):
            return

    await state.set_state(AddApplicationState.choosing_app_address)
    await message.answer(add_states_strings[AddApplicationState.choosing_app_address])


@router.message(StateFilter(AddApplicationState.choosing_app_address), F.text)
async def choosing_app_address(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AddApplicationState.choosing_app_machine)
        await message.answer(add_states_strings[AddApplicationState.choosing_app_machine])
        return

    if message.text != "Далее":
        if not await parse_app_address(message, state):
            return

    await state.set_state(AddApplicationState.writing_app_est_repair_date_and_duration)
    await message.answer(add_states_strings[AddApplicationState.writing_app_est_repair_date_and_duration])


@router.message(StateFilter(AddApplicationState.writing_app_est_repair_date_and_duration), F.text)
async def writing_app_est_repair_date_and_duration(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AddApplicationState.choosing_app_address)
        await message.answer(add_states_strings[AddApplicationState.choosing_app_address])
        return

    if message.text != "Далее":
        if not await parse_app_est_repair_date_and_duration(message, state):
            return

    await state.set_state(AddApplicationState.writing_app_notes)
    await message.answer(add_states_strings[AddApplicationState.writing_app_notes])


@router.message(StateFilter(AddApplicationState.writing_app_notes), F.text)
async def writing_app_notes(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AddApplicationState.writing_app_est_repair_date_and_duration)
        await message.answer(add_states_strings[AddApplicationState.writing_app_est_repair_date_and_duration])
        return

    if message.text != "Далее":
        await state.update_data(notes=message.text)

    app_data = await state.get_data()
    app_data["editor_id"] = message.from_user.id
    app_reasons: list[str] | None = app_data.get("app_reasons")
    if app_reasons is None:
        app_reasons = list()
    try:
        application = ApplicationAdd.model_validate(app_data)
    except ValidationError as e:
        await message.answer("Заполнены не все обязательные поля")
        await message.answer(add_states_strings[AddApplicationState.writing_app_notes])
        return

    await message.answer(
        f"Клиент: {application.client_name}\n"
        f"id контакта: {application.contact_id}\n"
        f"Причины заявки: {"; ".join(app_reasons)}\n"
        f"Станок: {application.machine_name}\n"
        f"Адрес: {application.address_name}\n"
        f"Примерная дата ремонта: {application.est_repair_date}\n"
        f"Примерное время ремонта: {application.est_repair_duration_hours}\n"
        f"Заметки: {application.notes}\n",
        reply_markup=render_inline_buttons(
            {"confirm_app_add": "Подтвердить", "cancel_app_add": "Отмена"}, 1
        )
    )
    await state.set_state(AddApplicationState.add_app_confirmation)


@router.callback_query(StateFilter(AddApplicationState.add_app_confirmation), F.data == "cancel_app_add")
async def add_app_confirmation_cancel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Отменено")
    await state.set_state(AddApplicationState.writing_app_notes)
    await callback_query.message.answer(add_states_strings[AddApplicationState.writing_app_notes])


@router.callback_query(StateFilter(AddApplicationState.add_app_confirmation), F.data == "confirm_app_add")
async def add_app_confirmation(callback_query: CallbackQuery, state: FSMContext):
    app_data = await state.get_data()

    app_data["editor_id"] = callback_query.from_user.id
    app_reasons: list[str] | None = app_data.get("app_reasons")
    if app_reasons is None:
        app_reasons = list()
    try:
        application = ApplicationAdd.model_validate(app_data)
    except ValidationError:
        await callback_query.answer("Заполнены не все обязательные поля")
        await add_app_confirmation_cancel(callback_query, state)
        return

    if not await db_apps.add_application(application, app_reasons):
        await callback_query.answer("Что-то пошло не так(")
        await add_app_confirmation_cancel(callback_query, state)
        return

    await callback_query.answer("Заявка добавлена")
    await callback_query.message.answer(
        text="Выберите действие",
        reply_markup=render_keyboard_buttons(base_commands, 2)
    )
    await state.clear()
