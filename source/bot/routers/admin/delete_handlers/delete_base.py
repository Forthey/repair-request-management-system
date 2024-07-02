from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.commands import base_commands
from bot.routers.utility_commands.back import back
from bot.utility.entities_to_str.address_to_str import address_to_str
from bot.utility.entities_to_str.client_to_str import client_to_str
from bot.utility.entities_to_str.contact_to_str import contact_to_str
from bot.utility.entities_to_str.machine_to_str import machine_to_str
from bot.utility.render_buttons import render_inline_buttons, render_keyboard_buttons

from bot.states.delete import DeleteState
from database.queries.addresses import address_belongs_to_client, get_address, check_if_address_safe_to_delete, \
    delete_address
from database.queries.clients import check_if_client_safe_to_delete, get_client, delete_client
from database.queries.contacts import get_contact, check_if_contact_safe_to_delete, delete_contact
from database.queries.machines import get_machine, check_if_machine_safe_to_delete, delete_machine

router = Router()


buttons = [
    "Отмена"
]

deletable_entities = {
    "delete_client": "Клиент",
    "delete_address": "Адрес",
    "delete_contact": "Контакт",
    "delete_machine": "Станок",
    # "delete_other": "Другое"
}


@router.message(StateFilter(None), F.text == "Удалить объект")
@router.message(StateFilter(None), Command("delete"))
async def delete_base(message: Message, state: FSMContext):
    await message.answer(
        text="Удаление объекта",
        reply_markup=render_keyboard_buttons(buttons, 1)
    )
    await message.answer(
        text="Выберите объект для удаления",
        reply_markup=render_inline_buttons(deletable_entities, 2)
    )
    await state.set_state(DeleteState.choosing_entity)


#
# Delete client handlers
#
@router.callback_query(StateFilter(DeleteState.choosing_entity), F.data == "delete_client")
async def delete_client_callback(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Введите имя клиента")
    await state.set_state(DeleteState.choosing_client_name_to_delete)


@router.message(StateFilter(DeleteState.choosing_client_name_to_delete), F.text)
async def delete_client_by_name(message: Message, state: FSMContext):
    client_name = message.text

    client = await get_client(client_name)

    if not client:
        await message.answer(f"Клиента '{client_name}' не существует")
        return
    if not await check_if_client_safe_to_delete(client_name):
        await message.answer("Нельзя безопасно удалить клиента")
        return

    await state.update_data(client_name=client_name)
    await message.answer(
        text=client_to_str(client),
        reply_markup=render_inline_buttons({"delete_client_confirmation": "Удалить"}, 1)
    )
    await state.set_state(DeleteState.delete_client_confirmation)


@router.callback_query(StateFilter(DeleteState.delete_client_confirmation), F.data == "delete_client_confirmation")
async def delete_client_by_name_confirmation(query: CallbackQuery, state: FSMContext):
    client_name = (await state.get_data()).get("client_name")
    if not client_name:
        await query.answer("Что-то пошло не так...")
    else:
        await delete_client(client_name)
        await query.answer(f"Клиент {client_name} удален")
    if not await back(state):
        await query.message.answer(
            "Выберите действие",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )


#
# Delete address handlers
#
@router.callback_query(StateFilter(DeleteState.choosing_entity), F.data == "delete_address")
async def delete_address_callback(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        "Введите имя клиента, к которому привязан адрес (или напишите \"Далее\", если адрес не привязан к клиенту)"
    )
    await state.set_state(DeleteState.choosing_client_name_to_address)


@router.message(StateFilter(DeleteState.choosing_client_name_to_address), F.text)
async def choose_client_to_address(message: Message, state: FSMContext):
    if message.text != "Далее":
        client_name = message.text
        client = await get_client(client_name)
        if not client:
            await message.answer(f"Клиента '{client_name}' не существует")
            return

        await state.update_data(client_name=client_name)

    await message.answer("Введите адрес")
    await state.set_state(DeleteState.choosing_address_name_to_delete)


@router.message(StateFilter(DeleteState.choosing_address_name_to_delete), F.text)
async def delete_address_by_name(message: Message, state: FSMContext):
    address_name = message.text
    client_name = (await state.get_data()).get("client_name")
    address = await get_address(client_name, address_name)

    if not address:
        await message.answer(f"Адреса '{address_name}' у клиента '{client_name if client_name else ""}' не существует")
        return
    if not await check_if_address_safe_to_delete(client_name, address_name):
        await message.answer("Нельзя безопасно удалить адрес")
        return

    await state.update_data(address_name=address_name)
    await message.answer(
        text=address_to_str(address),
        reply_markup=render_inline_buttons({"delete_address_confirmation": "Удалить"}, 1)
    )
    await state.set_state(DeleteState.delete_address_confirmation)


@router.callback_query(StateFilter(DeleteState.delete_address_confirmation), F.data == "delete_address_confirmation")
async def delete_address_by_name_confirmation(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    address_name = data.get("address_name")
    client_name = data.get("client_name")
    if not address_name:
        await query.answer("Что-то пошло не так...")
    else:
        await delete_address(client_name, address_name)
        await query.answer(f"Адрес {address_name} удален")
    if not await back(state):
        await query.message.answer(
            "Выберите действие",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )


#
# Delete contact handlers
#
@router.callback_query(StateFilter(DeleteState.choosing_entity), F.data == "delete_contact")
async def delete_contact_callback(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Введите id контакта")
    await state.set_state(DeleteState.choosing_contact_id_to_delete)


@router.message(StateFilter(DeleteState.choosing_contact_id_to_delete), F.text)
async def delete_contact_by_id(message: Message, state: FSMContext):
    contact_id: str | int = message.text
    try:
        contact_id = int(contact_id)
    except ValueError:
        await message.answer("Указан не id")
        return

    contact = await get_contact(contact_id)
    if not contact:
        await message.answer(f"Контакта с id '{contact_id}' не существует")
        return
    if not await check_if_contact_safe_to_delete(contact_id):
        await message.answer("Нельзя безопасно удалить контакт")
        return

    await state.update_data(contact_id=contact_id)
    await message.answer(
        text=contact_to_str(contact),
        reply_markup=render_inline_buttons({"delete_contact_confirmation": "Удалить"}, 1)
    )
    await state.set_state(DeleteState.delete_contact_confirmation)


@router.callback_query(StateFilter(DeleteState.delete_contact_confirmation), F.data == "delete_contact_confirmation")
async def delete_contact_by_name_confirmation(query: CallbackQuery, state: FSMContext):
    contact_id = (await state.get_data()).get("contact_id")
    if not contact_id:
        await query.answer("Что-то пошло не так...")
    else:
        await delete_contact(contact_id)
        await query.answer(f"Контакт {contact_id} удален")
    if not await back(state):
        await query.message.answer(
            "Выберите действие",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )


#
# Delete machine handlers
#
@router.callback_query(StateFilter(DeleteState.choosing_entity), F.data == "delete_machine")
async def delete_machine_callback(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Введите название станка")
    await state.set_state(DeleteState.choosing_machine_name_to_delete)


@router.message(StateFilter(DeleteState.choosing_machine_name_to_delete), F.text)
async def delete_machine_by_name(message: Message, state: FSMContext):
    machine_name = message.text
    machine = await get_machine(machine_name)
    if not machine:
        await message.answer(f"Станка '{machine_name}' не существует")
        return
    if not await check_if_machine_safe_to_delete(machine_name):
        await message.answer("Нельзя безопасно удалить станок")
        return

    await state.update_data(machine_name=machine_name)
    await message.answer(
        text=machine_to_str(machine),
        reply_markup=render_inline_buttons({"delete_machine_confirmation": "Удалить"}, 1)
    )
    await state.set_state(DeleteState.delete_machine_confirmation)


@router.callback_query(StateFilter(DeleteState.delete_machine_confirmation), F.data == "delete_machine_confirmation")
async def delete_machine_by_name_confirmation(query: CallbackQuery, state: FSMContext):
    machine_name = (await state.get_data()).get("machine_name")
    if not machine_name:
        await query.answer("Что-то пошло не так...")
    else:
        await delete_machine(machine_name)
        await query.answer(f"Станок '{machine_name}' удален")
    if not await back(state):
        await query.message.answer(
            "Выберите действие",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )


#
# Delete other handler
#
deletable_other_entities = {
    "delete_company_position": "Должность в компании",
    "delete_close_reason": "Причина закрытия заявки",
    "delete_company_activity": "Деятельность компании",
    "go_back_to_main_delete": "Назад"
}


@router.callback_query(StateFilter(DeleteState.choosing_entity), F.data == "delete_other")
async def delete_other_callback(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        text="Выберите объект для удаления",
        reply_markup=render_inline_buttons(deletable_other_entities, 1)
    )


@router.callback_query(StateFilter(DeleteState.choosing_entity), F.data == "go_back_to_main_delete")
async def go_back_to_main_delete_callback(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        text="Выберите объект для удаления",
        reply_markup=render_inline_buttons(deletable_entities, 2)
    )
