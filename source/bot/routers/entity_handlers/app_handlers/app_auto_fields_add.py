from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.routers.entity_handlers.app_handlers.edit_app import print_edit_message
from bot.states.application import AddApplicationState, EditApplicationState, add_states_strings, edit_states_strings
from database.queries.addresses import add_address, get_address
from database.queries.clients import add_client
from database.queries.machines import add_machine, get_machine
from schemas.addresses import AddressAdd
from schemas.clients import ClientAdd

router = Router()


@router.callback_query(StateFilter(AddApplicationState.choosing_app_client), F.data == "yes_to_add_client")
async def create_and_add_client(query: CallbackQuery, state: FSMContext):
    new_client_name: str | None = (await state.get_data()).get("tmp_client_name")
    if not new_client_name or not await add_client(ClientAdd(name=new_client_name)):
        await query.answer("Что-то пошло не так...")
        return
    await state.update_data(client_name=new_client_name)
    await state.update_data(tmp_client_name=None)

    await query.answer(f"Клиент {new_client_name} создан")
    await query.message.edit_text(
        f"Клиент {new_client_name} создан и добавлен к заявке",
        reply_markup=None
    )

    await state.set_state(AddApplicationState.choosing_app_contact)
    await query.message.answer(add_states_strings[AddApplicationState.choosing_app_contact])


@router.callback_query(StateFilter(AddApplicationState.choosing_app_client), F.data == "no_to_add_client")
async def decline_create_add_client(query: CallbackQuery, state: FSMContext):
    await state.update_data(tmp_client_name=None)
    await query.answer("Отменено")

    await query.message.edit_text(
        add_states_strings[AddApplicationState.choosing_app_client],
        reply_markup=None
    )


@router.callback_query(StateFilter(AddApplicationState.choosing_app_machine), F.data == "yes_to_add_machine")
@router.callback_query(StateFilter(EditApplicationState.choosing_app_machine), F.data == "yes_to_add_machine")
async def create_and_add_machine(query: CallbackQuery, state: FSMContext):
    new_machine_name: str | None = (await state.get_data()).get("tmp_machine_name")
    if not new_machine_name or not await add_machine(new_machine_name):
        await query.answer("Что-то пошло не так...")
        return
    await state.update_data(machine=(await get_machine(new_machine_name)))
    await state.update_data(machine_name=new_machine_name)
    await state.update_data(tmp_machine_name=None)

    await query.answer(f"Станок {new_machine_name} создан")
    await query.message.edit_text(
        f"Станок {new_machine_name} создан и добавлен к заявке",
        reply_markup=None
    )

    state_name = await state.get_state()
    if state_name == AddApplicationState.choosing_app_machine:
        await state.set_state(AddApplicationState.choosing_app_address)
        await query.message.answer(add_states_strings[AddApplicationState.choosing_app_address])
    elif state_name == EditApplicationState.choosing_app_machine:
        await state.set_state(EditApplicationState.waiting_for_click)
        await print_edit_message(query.message, state)


@router.callback_query(StateFilter(AddApplicationState.choosing_app_machine), F.data == "no_to_add_machine")
@router.callback_query(StateFilter(EditApplicationState.choosing_app_machine), F.data == "no_to_add_machine")
async def decline_create_add_machine(query: CallbackQuery, state: FSMContext):
    await state.update_data(tmp_machine_name=None)
    await query.answer("Отменено")

    state_name = await state.get_state()
    if state_name == AddApplicationState.choosing_app_machine:
        await query.message.edit_text(
            add_states_strings[AddApplicationState.choosing_app_machine],
            reply_markup=None
        )
    elif state_name == EditApplicationState.choosing_app_machine:
        await query.message.edit_text(
            edit_states_strings[EditApplicationState.choosing_app_machine],
            reply_markup=None
        )


@router.callback_query(StateFilter(AddApplicationState.choosing_app_address), F.data == "yes_to_add_address")
@router.callback_query(StateFilter(EditApplicationState.choosing_app_address), F.data == "yes_to_add_address")
async def create_and_add_address(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_address_name: str | None = data.get("tmp_address_name")
    client_name: str | None = data.get("client_name")

    if (not new_address_name or not client_name or
            not await add_address(AddressAdd(name=new_address_name, client_name=client_name))):
        await query.answer("Что-то пошло не так...")
        return

    await state.update_data(address=(await get_address(client_name, new_address_name)))
    await state.update_data(address_name=new_address_name)
    await state.update_data(tmp_address_name=None)

    await query.answer(f"Адрес {new_address_name} создан")
    await query.message.edit_text(
        f"Адрес {new_address_name} создан и добавлен к заявке",
        reply_markup=None
    )

    state_name = await state.get_state()
    if state_name == AddApplicationState.choosing_app_address:
        await state.set_state(AddApplicationState.writing_app_est_repair_date_and_duration)
        await query.message.answer(add_states_strings[AddApplicationState.writing_app_est_repair_date_and_duration])
    elif state_name == EditApplicationState.choosing_app_address:
        await state.set_state(EditApplicationState.waiting_for_click)
        await print_edit_message(query.message, state)


@router.callback_query(StateFilter(AddApplicationState.choosing_app_address), F.data == "no_to_add_address")
@router.callback_query(StateFilter(EditApplicationState.choosing_app_address), F.data == "no_to_add_address")
async def decline_create_add_address(query: CallbackQuery, state: FSMContext):
    await state.update_data(tmp_address_name=None)
    await query.answer("Отменено")

    state_name = await state.get_state()
    if state_name == AddApplicationState.choosing_app_address:
        await query.message.edit_text(
            add_states_strings[AddApplicationState.choosing_app_address],
            reply_markup=None
        )
    elif state_name == EditApplicationState.choosing_app_address:
        await query.message.edit_text(
            edit_states_strings[EditApplicationState.choosing_app_address],
            reply_markup=None
        )
