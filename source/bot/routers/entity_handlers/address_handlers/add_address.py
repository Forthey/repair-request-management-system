import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from pydantic import ValidationError

from bot.commands import base_commands
from bot.routers.utility_commands.back import back
from bot.states.address import AddressState
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
import database.queries.clients as db_clients
import database.queries.addresses as db_addresses
from schemas.addresses import AddressAdd, Address


router = Router()


commands = [
    "Далее",
    "Назад",
    "Отмена"
]

states_strings: dict[str, str] = {
    AddressState.writing_address: "Введите адрес",
    AddressState.choosing_client: "Выберите компанию (клиента)",
    AddressState.choosing_photo: "Загрузите фото адреса",
    AddressState.writing_workhours: "Введите часы работы предприятия по адресу в формате XX:XX-XX:XX",
    AddressState.writing_notes: "Напишите какую-нибудь дополнительную информацию, если необходимо"
}


@router.message(StateFilter(None), F.text.lower() == "добавить адрес")
async def add_address(message: Message, state: FSMContext):
    await message.answer(
        text="Создание нового адреса",
        reply_markup=render_keyboard_buttons(commands, 2)
    )

    await message.answer(states_strings[AddressState.writing_address])
    await state.set_state(AddressState.writing_address)


@router.message(StateFilter(AddressState.writing_address), F.text)
async def writing_address(message: Message, state: FSMContext):
    if message.text == "Далее":
        await state.set_state(AddressState.choosing_client)
        await message.answer(states_strings[AddressState.choosing_client])
        return

    if message.text == "Назад":
        await message.answer("Это первое поле")
        return

    address = message.text
    if await db_addresses.find_address(address):
        await message.answer("Такой адрес уже существует")
        return

    await state.update_data(name=address)

    await state.set_state(AddressState.choosing_client)
    await message.answer(states_strings[AddressState.choosing_client])


@router.message(StateFilter(AddressState.choosing_client), F.text)
async def choosing_client(message: Message, state: FSMContext):
    if message.text == "Далее":
        await state.set_state(AddressState.choosing_photo)
        await message.answer(states_strings[AddressState.choosing_photo])
        return

    if message.text == "Назад":
        await state.set_state(AddressState.writing_address)
        await message.answer(states_strings[AddressState.writing_address])
        return

    client_name = message.text
    if not await db_clients.find_client(client_name):
        await message.answer("Такого клиента не существует")
        return

    await state.update_data(client_name=client_name)

    await state.set_state(AddressState.choosing_photo)
    await message.answer(states_strings[AddressState.choosing_photo])


@router.message(StateFilter(AddressState.choosing_photo), F.photo)
async def choosing_photo(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AddressState.choosing_client)
        await message.answer(states_strings[AddressState.choosing_client])
        return

    if message.text != "Далее":
        file_id = message.photo[0].file_id
        await state.update_data(photo_url=file_id)

    await state.set_state(AddressState.writing_workhours)
    await message.answer(states_strings[AddressState.writing_workhours])


@router.message(StateFilter(AddressState.writing_workhours), F.text)
async def writing_workhours(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AddressState.choosing_photo)
        await message.answer(states_strings[AddressState.choosing_photo])
        return

    if message.text != "Далее":
        if not re.match(r"([01][0-9]|2[0-3]):[0-5][0-9]-([01]?[0-9]|2[0-3]):[0-5][0-9]", message.text):
            await message.answer(
                f"Неверный формат\n"
                f"{states_strings[AddressState.writing_workhours]}"
            )
            return

        await state.update_data(workhours=message.text)

    await state.set_state(AddressState.writing_notes)
    await message.answer(states_strings[AddressState.writing_notes])


@router.message(StateFilter(AddressState.writing_notes), F.text)
async def writing_notes(message: Message, state: FSMContext):
    if message.text == "Назад":
        await state.set_state(AddressState.choosing_photo)
        await message.answer(states_strings[AddressState.choosing_photo])
        return

    if message.text != "Далее":
        await state.update_data(notes=message.text)

    try:
        address = AddressAdd.model_validate(await state.get_data(), from_attributes=True)
    except ValidationError:
        await message.answer(
            f"Есть незаполненные обязательные поля\n"
        )
        return

    await state.set_state(AddressState.add_address_confirmation)
    await message.answer(
        f"Адрес: {address.name}\n"
        f"Клиент: {address.client_name}\n"
        f"Часы работы: {address.workhours}\n"
        f"Заметки: {address.notes}\n",
        reply_markup=render_inline_buttons({"confirm_addr_add": "Подтвердить", "cancel_addr_add": "Отмена"}, 1)
    )


@router.callback_query(StateFilter(AddressState.add_address_confirmation), F.data == "cancel_addr_add")
async def cancel_confirmation(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(AddressState.writing_notes)
    await callback_query.answer("Отменено")
    await callback_query.message.answer(states_strings[AddressState.writing_notes])


@router.callback_query(StateFilter(AddressState.add_address_confirmation), F.data == "confirm_addr_add")
async def add_address_confirmation(callback_query: CallbackQuery, state: FSMContext):
    address = AddressAdd.model_validate(await state.get_data(), from_attributes=True)

    if not await db_addresses.add_address(address):
        await callback_query.answer("Адрес уже существует")
        await cancel_confirmation(callback_query, state)
        return

    await callback_query.answer("Адрес добавлен")
    if not await back(state):
        await callback_query.message.answer(
            "Выберите действие",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )
