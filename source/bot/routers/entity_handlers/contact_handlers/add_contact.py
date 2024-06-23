import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from pydantic import ValidationError

from bot.commands import base_commands
from bot.routers.utility_commands.back import back
from bot.states.contact import ContactState
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
import database.queries.contacts as db_contacts
import database.queries.clients as db_clients
import database.queries.other as db_other
from schemas.contacts import ContactAdd

router = Router()

commands = [
    "Далее",
    "Назад",
    "Отмена"
]


states_strings: dict[str, str] = {
    ContactState.writing_contact_fio: "Введите ФИО в формате: Имя Фамилия Отчество. Необходимо указать хотя бы имя",
    ContactState.writing_contact_client_name: "Выберите компанию, к которой будет привязан этот контакт",
    ContactState.choosing_contact_company_position: "Введите должность (или создайте с помощью new 'должность')",
    ContactState.writing_contact_email: "Введите email",
    ContactState.writing_contact_phone_numbers: "Введите до 3х номеров в формате +7XXXXXXXXXX"
}


@router.message(StateFilter(None), F.text.lower() == "добавить контакт")
async def add_contact(message: Message, state: FSMContext):
    await message.answer(
        text="Создание нового контакта",
        reply_markup=render_keyboard_buttons(commands, 2)
    )
    await message.answer(states_strings[ContactState.writing_contact_fio])

    await state.set_state(ContactState.writing_contact_fio)


@router.message(StateFilter(ContactState.writing_contact_fio), F.text)
async def add_contact_fio(message: Message, state: FSMContext):
    if message.text == "Далее":
        await state.set_state(ContactState.writing_contact_client_name)
        await message.answer(states_strings[ContactState.writing_contact_client_name])
        return

    if message.text == "Назад":
        await message.answer("Это первое поле")
        return

    args = message.text.split(" ")

    if len(args) < 1:
        await message.answer("Укажите хотя бы фамилию")
        return

    if len(args) > 1:
        if len(args) > 2:
            if len(args) > 3:
                await message.answer(
                    f"Неправильный формат\n"
                    f"{states_strings[ContactState.writing_contact_fio]}"
                )
                return
            await state.update_data(patronymic=args[2])
        await state.update_data(surname=args[1])
    await state.update_data(name=args[0])

    await message.answer(states_strings[ContactState.writing_contact_client_name])
    await state.set_state(ContactState.writing_contact_client_name)


@router.message(StateFilter(ContactState.writing_contact_client_name), F.text)
async def add_contact_client_name(message: Message, state: FSMContext):
    if message.text == "Далее":
        await state.set_state(ContactState.choosing_contact_company_position)
        await message.answer(states_strings[ContactState.choosing_contact_company_position])
        return
    if message.text == "Назад":
        await state.set_state(ContactState.writing_contact_fio)
        await message.answer(states_strings[ContactState.writing_contact_fio])
        return

    if len(message.text) < 2:
        await message.answer("Слишком короткое имя")
        return

    client_name = message.text
    if not await db_clients.find_client(client_name):
        await message.answer(
            f"Клиента '{client_name}' не существует\n"
            f"{states_strings[ContactState.writing_contact_client_name]}"
        )
        return

    await state.update_data(client_name=client_name)

    await message.answer(states_strings[ContactState.choosing_contact_company_position])
    await state.set_state(ContactState.choosing_contact_company_position)


@router.message(StateFilter(ContactState.choosing_contact_company_position), F.text)
async def add_contact_company_position(message: Message, state: FSMContext):
    if message.text == "Далее":
        await state.set_state(ContactState.writing_contact_email)
        await message.answer(states_strings[ContactState.writing_contact_email])
        return
    if message.text == "Назад":
        await state.set_state(ContactState.writing_contact_client_name)
        await message.answer(states_strings[ContactState.writing_contact_client_name])
        return

    if len(message.text) < 2:
        await message.answer("Слишком короткое имя")
        return

    args = message.text.split(" ")
    if args[0] == "new":
        if len(args) < 2:
            await message.answer(
                f"Неверный формат\n"
                f"{states_strings[ContactState.choosing_contact_company_position]}"
            )
            return
        company_position = " ".join(args[1:])
        if await db_other.add_company_position(company_position) is None:
            await message.answer("Такая должность уже существует")
            return

        await message.answer(f"Должность {company_position} добавлена")
        await state.update_data(company_position=company_position)
    else:
        if not await db_other.find_company_position(message.text):
            await message.answer("Такой должности не существует")
            return
        await state.update_data(company_position=message.text)

    await message.answer(states_strings[ContactState.writing_contact_email])
    await state.set_state(ContactState.writing_contact_email)


@router.message(StateFilter(ContactState.writing_contact_email), F.text)
async def add_contact_email(message: Message, state: FSMContext):
    if message.text == "Далее":
        await state.set_state(ContactState.writing_contact_phone_numbers)
        await message.answer(states_strings[ContactState.writing_contact_phone_numbers])
        return
    if message.text == "Назад":
        await state.set_state(ContactState.writing_contact_client_name)
        await message.answer(states_strings[ContactState.writing_contact_client_name])
        return

    if len(message.text) < 2:
        await message.answer("Слишком короткая почта")
        return

    email = message.text
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await message.answer("У почты неверный формат. Проверьте и повторите попытку")
        return

    await state.update_data(email=email)

    await message.answer(states_strings[ContactState.writing_contact_phone_numbers])
    await state.set_state(ContactState.writing_contact_phone_numbers)


@router.message(StateFilter(ContactState.writing_contact_phone_numbers), F.text)
async def add_contact_phone_numbers(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(ContactState.writing_contact_email)
        await message.answer(states_strings[ContactState.writing_contact_email])
        return

    if len(message.text) < 2:
        await message.answer("Слишком короткий номер")
        return

    if message.text != "Далее":
        phones = message.text.split(" ")

        await state.update_data(
            phone1=phones[0],
            phone2=phones[1] if len(phones) == 2 else None,
            phone3=phones[2] if len(phones) == 3 else None
        )

    contact_data = await state.get_data()

    if not contact_data.get("phone1") and not contact_data.get("email"):
        await message.answer("Есть незаполненные обязательные поля")
        return

    try:
        contact = ContactAdd.model_validate(contact_data, from_attributes=True)
    except ValidationError:
        await message.answer(
            f"Есть незаполненные обязательные поля\n"
        )
        return

    await state.set_state(ContactState.add_contact_confirmation)
    await message.answer(
        f"ФИО: {contact.surname} {contact.name} {contact.patronymic}\n"
        f"Компания: {contact.client_name}\n"
        f"Должность: {contact.company_position}\n"
        f"Email: {contact.email}\n"
        f"Телефоны: {contact.phone1} {contact.phone2} {contact.phone3}",
        reply_markup=render_inline_buttons({"confirm_contact_add": "Подтвердить", "cancel_contact_add": "Отмена"}, 1)
    )


@router.callback_query(StateFilter(ContactState.add_contact_confirmation), F.data == "cancel_contact_add")
async def cancel_confirmation(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(ContactState.writing_contact_phone_numbers)
    await callback_query.answer("Отменено")
    await callback_query.message.answer(states_strings[ContactState.writing_contact_phone_numbers])


@router.callback_query(StateFilter(ContactState.add_contact_confirmation), F.data == "confirm_contact_add")
async def add_contact_confirmation(callback_query: CallbackQuery, state: FSMContext):
    contact_data = await state.get_data()
    contact = ContactAdd.model_validate(contact_data, from_attributes=True)

    if not await db_contacts.add_contact(contact):
        await callback_query.answer("Что-то пошло не так...")
        await cancel_confirmation(callback_query, state)
        return

    await callback_query.answer("Контакт добавлен")
    if not await back(state):
        await callback_query.message.answer(
            "Выберите действие",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )
