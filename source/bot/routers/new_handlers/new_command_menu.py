from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.routers.entity_handlers.address_handlers.add_address import add_address
from bot.routers.entity_handlers.client_handlers.add_client import add_client
from bot.routers.entity_handlers.contact_handlers.add_contact import add_contact
from bot.routers.entity_handlers.machine_handlers import add_machine
from bot.states.new import NewState
from bot.utility.render_buttons import render_inline_buttons

# Router
router = Router()


buttons = {
    "add_client_via_new": "Клиент",
    "add_contact_via_new": "Контакт",
    "add_machine_via_new": "Станок",
    "add_address_via_new": "Адрес"
}

button_data_to_function = {
    "add_client_via_new": add_client,
    "add_contact_via_new": add_contact,
    "add_machine_via_new": add_machine,
    "add_address_via_new": add_address
}


@router.message(F.text == "/new")
async def show_new_command_menu(message: Message, state: FSMContext):
    data = await state.get_data()

    if data.get("__old_data") or data.get("__old_state"):
        await message.answer("Нельзя использовать команду /new здесь")
        return

    current_state = await state.get_state()
    await state.clear()

    await state.set_state(NewState.choosing_entity)
    await state.update_data(__old_state=current_state, __old_data=data)
    await message.answer(text="Добавление", reply_markup=render_inline_buttons(buttons, 2))


@router.callback_query(StateFilter(NewState.choosing_entity))
async def new_command_menu_callback(query: CallbackQuery, state: FSMContext):
    function = button_data_to_function.get(query.data)
    if function:
        await function(query.message, state)
