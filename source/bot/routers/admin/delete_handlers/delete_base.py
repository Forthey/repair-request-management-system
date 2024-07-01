from aiogram import Router, F
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.commands import base_commands
from bot.routers.utility_commands.back import back
from bot.utility.entities_to_str.client_to_str import client_to_str
from bot.utility.render_buttons import render_inline_buttons, render_keyboard_buttons

from bot.states.delete import DeleteState
from database.queries.clients import check_if_client_safe_to_delete, get_client, delete_client

router = Router()


buttons = [
    "Отмена"
]

deletable_entities = {
    "delete_client": "Клиент",
    "delete_address": "Адрес",
    "delete_contact": "Контакт",
    "delete_machine": "Станок",
    "delete_other": "Другое"
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
    ...


#
# Delete contact handlers
#
@router.callback_query(StateFilter(DeleteState.choosing_entity), F.data == "delete_contact")
async def delete_contact_callback(query: CallbackQuery, state: FSMContext):
    ...


#
# Delete machine handlers
#
@router.callback_query(StateFilter(DeleteState.choosing_entity), F.data == "delete_machine")
async def delete_machine_callback(query: CallbackQuery, state: FSMContext):
    ...


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
