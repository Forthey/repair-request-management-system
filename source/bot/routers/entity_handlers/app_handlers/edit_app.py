import datetime
import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.commands import base_commands
from bot.states.application import EditApplicationState, ChooseOneApplicationState
from bot.utility.entities_to_str.app_to_str import full_app_to_str, app_to_str
from bot.utility.render_buttons import render_inline_buttons, render_keyboard_buttons

from database.queries.applications import get_application
from schemas.applications import ApplicationFull

import database.queries.applications as db_apps
import database.queries.clients as db_clients
import database.queries.contacts as db_contacts
import database.queries.machines as db_machines
import database.queries.addresses as db_addresses
import database.queries.other as db_other


edit_field = {
    "edit_contact": "Контакт",
    # "edit_reasons": "Причины",
    "edit_machine": "Станок",
    "edit_address": "Адрес",
    "edit_est_rep_date_duration": "Дата и время ремонта",
    "edit_app_confirm": "Подвердить",
}

router = Router()

states_strings: dict[str, str] = {
    EditApplicationState.choosing_app_contact:
        "Введите id контакта, привязанного к клиенту "
        "(или создайте новый контакт, используя команду new)",
    EditApplicationState.choosing_app_reasons:
        "Введите причины подачи заявки (когда закончите - нажмите 'Далее')",
    EditApplicationState.choosing_app_machine:
        "Введите название станка",
    EditApplicationState.choosing_app_address:
        "Введите адрес, на который необходимо будет выехать "
        "(или привяжите новые адрес к компании, используя команду new: "
        "new адрес Пример Адреса)",
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
async def confirm_edit_app(query: CallbackQuery, state: FSMContext):
    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(query.message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_contact")
async def edit_app_contact(query: CallbackQuery, state: FSMContext):
    await query.message.answer(states_strings[EditApplicationState.choosing_app_contact])
    await state.set_state(EditApplicationState.choosing_app_contact)


@router.message(StateFilter(EditApplicationState.choosing_app_contact), F.text)
async def choosing_app_contact(message: Message, state: FSMContext):
    contact_id = message.text
    try:
        contact_id = int(contact_id)
    except ValueError:
        await message.answer("Указан не id")
        return
    if not await db_contacts.contact_exists(int(contact_id)):
        await message.answer("Контакта с таким id не существует")
        return
    await state.update_data(contact_id=contact_id)

    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(message)


# TODO изменения причин
# @router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_reasons")
# async def edit_app_reasons(query: CallbackQuery, state: FSMContext):
#     await query.message.answer(states_strings[EditApplicationState.choosing_app_reasons])
#     await state.set_state(EditApplicationState.choosing_app_reasons)
#
#
# @router.message(StateFilter(EditApplicationState.choosing_app_reasons), F.text)
# async def choosing_app_reasons(message: Message, state: FSMContext):
#     reason = message.text
#     if not await db_other.find_app_reason(reason):
#         await message.answer("Такой причины не существует")
#         return
#     reasons = (await state.get_data()).get("app_reasons")
#     if reasons is None:
#         reasons: list[str] = [reason]
#     else:
#         reasons.append(reason)
#     await state.update_data(app_reasons=reasons)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_machine")
async def edit_app_contact(query: CallbackQuery, state: FSMContext):
    await query.message.answer(states_strings[EditApplicationState.choosing_app_machine])
    await state.set_state(EditApplicationState.choosing_app_machine)


@router.message(StateFilter(EditApplicationState.choosing_app_machine), F.text)
async def choosing_app_machine(message: Message, state: FSMContext):
    machine = message.text
    if not await db_machines.find_machine(machine):
        await message.answer("Такого станка не существует")
        return

    await state.update_data(machine_name=machine)

    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_address")
async def edit_app_contact(query: CallbackQuery, state: FSMContext):
    await query.message.answer(states_strings[EditApplicationState.choosing_app_address])
    await state.set_state(EditApplicationState.choosing_app_address)


@router.message(StateFilter(EditApplicationState.choosing_app_address), F.text)
async def choosing_app_address(message: Message, state: FSMContext):
    address = message.text
    if not await db_addresses.address_exists(address):
        await message.answer("Такого адреса не существует")
        return

    await state.update_data(address_name=address)

    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_est_rep_date_duration")
async def edit_app_contact(query: CallbackQuery, state: FSMContext):
    await query.message.answer(states_strings[EditApplicationState.editing_app_est_repair_date_and_duration])
    await state.set_state(EditApplicationState.editing_app_est_repair_date_and_duration)


@router.message(StateFilter(EditApplicationState.editing_app_est_repair_date_and_duration), F.text)
async def writing_app_est_repair_date_and_duration(message: Message, state: FSMContext):
    args = message.text.split(" ")
    if not (1 <= len(args) <= 2):
        await message.answer("Неправильный формат")
        return
    if len(args) > 0 and re.match(r"^[0-3][0-9].[0-1][0-9].20[2-9][0-9]$", args[0]):
        date_args = args[0].split(".")
        est_repair_date = datetime.datetime(int(date_args[2]), int(date_args[1]), int(date_args[0]))
        await state.update_data(est_repair_date=est_repair_date)
    if len(args) > 1:
        await state.update_data(est_repair_duration_hours=args[1])

    await state.set_state(EditApplicationState.waiting_for_click)
    await print_edit_message(message)


@router.callback_query(StateFilter(EditApplicationState.waiting_for_click), F.data == "edit_notes")
async def edit_app_contact(query: CallbackQuery, state: FSMContext):
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

    app: ApplicationFull | None = await get_application(edited_data["app_id"])

    if len(edited_data) == 1 or (len(edited_data) == 2 and edited_data.get("app_list_offset") is not None):
        await query.answer("Вы не изменили ни одно поле")
        return

    answer_result = (
        f"{app_to_str(app)}\n"
        f"\nИзмененные поля: \n"
    )

    for key in edited_data:
        if key == "app_id" or key == "app_list_offset":
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
async def cancel_app_edit(query: CallbackQuery, state: FSMContext):
    edited_data = await state.get_data()
    app_id = edited_data.pop("app_id")
    edited_data.pop("app_list_offset", 0)

    await db_apps.update_application(app_id, **edited_data)

    await state.clear()
    await query.answer("Заявка изменена")
    await query.message.answer("Выберите действие", reply_markup=render_keyboard_buttons(base_commands, 2))
