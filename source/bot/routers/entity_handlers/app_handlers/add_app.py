import datetime
import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from pydantic import ValidationError

from bot.commands import base_commands
from bot.state_watchers.application import ApplicationState
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
from bot.utility.get_id_by_username import get_user_id
import database.queries.applications as db_apps
import database.queries.clients as db_clients
import database.queries.contacts as db_contacts
import database.queries.machines as db_machines
import database.queries.addresses as db_addresses
import database.queries.workers as db_workers
import database.queries.other as db_other
from schemas.applications import ApplicationAdd
from schemas.clients import Client, ClientAdd
from schemas.other import ApplicationReason


ApplicationAdd.model_rebuild()

router = Router()

commands = [
    "Далее",
    "Назад",
    "Отмена"
]


states_strings: dict[str, str] = {
    ApplicationState.choosing_app_client: "Введите имя клиента (компании), подавшего заявку",
    ApplicationState.choosing_app_contact: "Введите id контакта, привязанного к клиенту",
    ApplicationState.choosing_app_reasons: "Введите причины подачи заявки (когда закончите - нажмите 'Далее')",
    ApplicationState.choosing_app_machine: "Введите название станка",
    ApplicationState.choosing_app_address: "Введите адрес, на который необходимо будет выехать",
    ApplicationState.writing_app_est_repair_date_and_duration: "Введите примерную дату ремонта (формат XX.XX.XXXX) "
                                                               "и через пробел примерное время, необходимое на ремонт (в часах)",
    ApplicationState.writing_app_notes: "Напишите допольнительную информацию, которую не удалось поместить в поля выше",
    ApplicationState.choosing_app_repairer: "Выберите того, кто возьмет заявку на ремонт"
}


@router.message(StateFilter(None), F.text.lower() == "добавить заявку")
async def add_client(message: Message, state: FSMContext):
    await message.answer(
        text="Создание новой заявки",
        reply_markup=render_keyboard_buttons(commands, 2)
    )

    await message.answer(states_strings[ApplicationState.choosing_app_client])
    await state.set_state(ApplicationState.choosing_app_client)


@router.message(StateFilter(ApplicationState.choosing_app_client), F.text)
async def choosing_app_client(message: Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Это первое поле")
        return

    if message.text != "Далее":
        client_name = message.text
        if not await db_clients.name_exists(client_name):
            await message.answer("Такого клиента не существует")
            return

        await state.update_data(client_name=client_name)

    await state.set_state(ApplicationState.choosing_app_contact)
    await message.answer(states_strings[ApplicationState.choosing_app_contact])


@router.message(StateFilter(ApplicationState.choosing_app_contact), F.text)
async def choosing_app_contact(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(ApplicationState.choosing_app_client)
        await message.answer(states_strings[ApplicationState.choosing_app_client])
        return

    if message.text != "Далее":
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

    await state.set_state(ApplicationState.choosing_app_reasons)
    await message.answer(states_strings[ApplicationState.choosing_app_reasons])


@router.message(StateFilter(ApplicationState.choosing_app_reasons), F.text)
async def choosing_app_reasons(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(ApplicationState.choosing_app_contact)
        await message.answer(states_strings[ApplicationState.choosing_app_contact])
        return

    if message.text == "Далее":
        await state.set_state(ApplicationState.choosing_app_machine)
        await message.answer(states_strings[ApplicationState.choosing_app_machine])
        return

    reason = message.text
    if not await db_other.find_app_reason(reason):
        await message.answer("Такой причины не существует")
        return
    reasons = (await state.get_data()).get("app_reasons")
    if reasons is None:
        reasons: list[str] = [reason]
    else:
        reasons.append(reason)
    await state.update_data(app_reasons=reasons)


@router.message(StateFilter(ApplicationState.choosing_app_machine), F.text)
async def choosing_app_machine(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(ApplicationState.choosing_app_reasons)
        await message.answer(states_strings[ApplicationState.choosing_app_reasons])
        return

    if message.text != "Далее":
        machine = message.text
        if not await db_machines.find_machine(machine):
            await message.answer("Такого станка не существует")
            return

        await state.update_data(machine=machine)

    await state.set_state(ApplicationState.choosing_app_address)
    await message.answer(states_strings[ApplicationState.choosing_app_address])


@router.message(StateFilter(ApplicationState.choosing_app_address), F.text)
async def choosing_app_address(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(ApplicationState.choosing_app_machine)
        await message.answer(states_strings[ApplicationState.choosing_app_machine])
        return

    if message.text != "Далее":
        address = message.text
        if not await db_addresses.address_exists(address):
            await message.answer("Такого адреса не существует")
            return

        await state.update_data(address=address)

    await state.set_state(ApplicationState.writing_app_est_repair_date_and_duration)
    await message.answer(states_strings[ApplicationState.writing_app_est_repair_date_and_duration])


@router.message(StateFilter(ApplicationState.writing_app_est_repair_date_and_duration), F.text)
async def writing_app_est_repair_date_and_duration(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(ApplicationState.choosing_app_address)
        await message.answer(states_strings[ApplicationState.choosing_app_address])
        return

    if message.text != "Далее":
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

    await state.set_state(ApplicationState.writing_app_notes)
    await message.answer(states_strings[ApplicationState.writing_app_notes])


@router.message(StateFilter(ApplicationState.writing_app_notes), F.text)
async def writing_app_notes(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(ApplicationState.writing_app_est_repair_date_and_duration)
        await message.answer(states_strings[ApplicationState.writing_app_est_repair_date_and_duration])
        return

    if message.text != "Далее":
        await state.update_data(notes=message.text)

    await state.set_state(ApplicationState.choosing_app_repairer)
    await message.answer(states_strings[ApplicationState.choosing_app_repairer])


@router.message(StateFilter(ApplicationState.choosing_app_repairer), F.text)
async def add_app_repairer(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(ApplicationState.writing_app_notes)
        await message.answer(states_strings[ApplicationState.writing_app_notes])
        return

    if message.text != "Далее":
        repairer_id = message.text
        try:
            repairer_id = int(repairer_id)
        except ValueError:
            await message.answer("Введён неверный id")
            return

        if not await db_workers.get_worker(repairer_id):
            await message.answer(f"Работника с id {repairer_id} не существует")
            return
        await state.update_data(repairer_id=repairer_id)

    app_data = await state.get_data()
    app_data["editor_id"] = message.from_user.id
    app_reasons: list[str] | None = app_data.get("app_reasons")
    if app_reasons is None:
        app_reasons = list()
    try:
        application = ApplicationAdd.model_validate(app_data)
    except ValidationError as e:
        print(app_data["app_reasons"])
        print(e)
        await message.answer("Заполнены не все обязательные поля")
        await message.answer(states_strings[ApplicationState.choosing_app_repairer])
        return

    await message.answer(
        text=f"id основной заявки: {application.main_application_id}\n"
             f"Клиент: {application.client_name}\n"
             f"id контакта: {application.contact_id}\n"
             f"Причины заявки: {"; ".join(app_reasons)}\n"
             f"Станок: {application.machine}\n"
             f"Адрес: {application.address}\n"
             f"Примерная дата ремонта: {application.est_repair_date}\n"
             f"Примерное время ремонта: {application.est_repair_duration_hours}\n"
             f"Заметки: {application.notes}\n"
             f"id работника, который будет заниматься ремонтом: {application.repairer_id}",
        reply_markup=render_inline_buttons(["Подтвердить", "Отмена"], 1)
    )
    await state.set_state(ApplicationState.add_app_confirmation)


@router.callback_query(StateFilter(ApplicationState.add_app_confirmation), F.data == "Отмена")
async def add_app_confirmation_cancel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Отменено")
    await state.set_state(ApplicationState.choosing_app_repairer)
    await callback_query.message.answer(states_strings[ApplicationState.choosing_app_repairer])


@router.callback_query(StateFilter(ApplicationState.add_app_confirmation), F.data == "Подтвердить")
async def add_app_confirmation(callback_query: CallbackQuery, state: FSMContext):
    app_data = await state.get_data()

    app_data["editor_id"] = (
        await db_workers.get_worker(callback_query.from_user.id)
    ).id
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
