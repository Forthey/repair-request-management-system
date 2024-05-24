import datetime
import logging
import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.commands import base_commands
from bot.routers.entity_handlers.app_handlers.app_fields_parser import parse_app_est_repair_date_and_duration, \
    parse_app_contact, parse_app_reason, parse_app_machine, parse_app_address
from bot.states.application import EditApplicationState, ChooseOneApplicationState
from bot.utility.entities_to_str.app_to_str import full_app_to_str, app_to_str
from bot.utility.render_buttons import render_inline_buttons, render_keyboard_buttons

from database.queries.applications import get_application
from schemas.applications import ApplicationFull

import database.queries.applications as db_apps


edit_field = {
    # "edit_client": "Клиент",
    "edit_contact": "Контакт",
    "edit_machine": "Станок",
    "edit_address": "Адрес",
    "edit_est_rep_date_duration": "Дата и время ремонта",
    "edit_app_confirm": "Подтвердить",
}

router = Router()

states_strings: dict[str, str] = {
    EditApplicationState.choosing_app_contact:
        "Введите id контакта, привязанного к клиенту "
        "(или привяжите новый контакт к клиенту, используя команду /add:\n"
        "/add Имя +790012088\n"
        "/add Имя example@gmail.com)\n",
    EditApplicationState.choosing_app_reasons:
        "Введите причину подачи заявки",
    EditApplicationState.choosing_app_machine:
        "Введите название станка",
    EditApplicationState.choosing_app_address:
        "Введите адрес, на который необходимо будет выехать "
        "(или привяжите новые адрес к компании, используя команду /add: "
        "/add Пример Адреса)",
    EditApplicationState.editing_app_est_repair_date_and_duration:
        "Введите примерную дату ремонта (формат XX.XX.XXXX) "
        "и через пробел примерное время, необходимое на ремонт (в часах) "
        "(Необязатльное поле)",
    EditApplicationState.editing_app_notes:
        "Напишите допольнительную информацию, которую не удалось поместить в поля выше"
        "(Необязательное поле)",
}


async def print_edit_message(message: Message):
    await message.answer(
        "Выберите поле для изменения",
        reply_markup=render_inline_buttons(edit_field, 2)
    )


@router.callback_query(StateFilter(ChooseOneApplicationState.chosen_app_confirmation), F.data == "confirm_edit_app")
async def confirm_edit_app_begin(query: CallbackQuery, state: FSMContext):
    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(query.message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_contact")
async def edit_app_contact(query: CallbackQuery, state: FSMContext):
    await query.message.answer(states_strings[EditApplicationState.choosing_app_contact])
    await state.set_state(EditApplicationState.choosing_app_contact)


@router.message(StateFilter(EditApplicationState.choosing_app_contact), F.text)
async def choosing_app_contact(message: Message, state: FSMContext):
    if not await parse_app_contact(message, state):
        return

    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_machine")
async def edit_app_machine(query: CallbackQuery, state: FSMContext):
    await query.message.answer(states_strings[EditApplicationState.choosing_app_machine])
    await state.set_state(EditApplicationState.choosing_app_machine)


@router.message(StateFilter(EditApplicationState.choosing_app_machine), F.text)
async def choosing_app_machine(message: Message, state: FSMContext):
    if not await parse_app_machine(message, state):
        return

    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_address")
async def edit_app_contact(query: CallbackQuery, state: FSMContext):
    await query.message.answer(states_strings[EditApplicationState.choosing_app_address])
    await state.set_state(EditApplicationState.choosing_app_address)


@router.message(StateFilter(EditApplicationState.choosing_app_address), F.text)
async def edit_address(message: Message, state: FSMContext):
    if not await parse_app_address(message, state):
        return

    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_est_rep_date_duration")
async def edit_est_rep_date_duration(query: CallbackQuery, state: FSMContext):
    await query.message.answer(states_strings[EditApplicationState.editing_app_est_repair_date_and_duration])
    await state.set_state(EditApplicationState.editing_app_est_repair_date_and_duration)


@router.message(StateFilter(EditApplicationState.editing_app_est_repair_date_and_duration), F.text)
async def writing_app_est_repair_date_and_duration(message: Message, state: FSMContext):
    if not await parse_app_est_repair_date_and_duration(message, state):
        return

    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_notes")
async def edit_app_notes(query: CallbackQuery, state: FSMContext):
    await query.message.answer(states_strings[EditApplicationState.editing_app_est_repair_date_and_duration])
    await state.set_state(EditApplicationState.editing_app_est_repair_date_and_duration)


@router.message(StateFilter(EditApplicationState.editing_app_notes), F.text)
async def writing_app_notes(message: Message, state: FSMContext):
    await state.update_data(notes=message.text)

    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_app_confirm")
async def edit_app_confirm(query: CallbackQuery, state: FSMContext):
    edited_data = await state.get_data()

    app: ApplicationFull | None = await get_application(edited_data["app_id"])\

    logging.info(edited_data)
    if len(edited_data) == 1:
        await query.answer("Вы не изменили ни одно поле")
        return

    answer_result = (
        f"{app_to_str(app)}\n"
        f"\nИзмененные поля: \n"
    )

    for key in edited_data:
        if key == "app_id":
            continue
        answer_result += f"{db_apps.changeable_app_field_to_str[key]}: {getattr(app, key)} -> {edited_data[key]}\n"

    await query.message.answer(
        answer_result,
        reply_markup=render_inline_buttons({"confirm_app_edit": "Подтвердить", "cancel_app_edit": "Отмена"}, 1)
    )
    await state.set_state(EditApplicationState.edit_app_confirmation)


@router.callback_query(StateFilter(EditApplicationState.edit_app_confirmation), F.data == "cancel_app_edit")
async def cancel_app_edit(query: CallbackQuery, state: FSMContext):
    await state.set_state(EditApplicationState.waiting_for_click)
    await query.answer("Отменено")
    await print_edit_message(query.message)


@router.callback_query(StateFilter(EditApplicationState.edit_app_confirmation), F.data == "confirm_app_edit")
async def confirm_app_edit(query: CallbackQuery, state: FSMContext):
    edited_data = await state.get_data()
    app_id = edited_data.pop("app_id")

    await db_apps.update_application(app_id, **edited_data)

    await state.clear()
    await query.answer("Заявка изменена")
    await query.message.answer("Выберите действие", reply_markup=render_keyboard_buttons(base_commands, 2))
