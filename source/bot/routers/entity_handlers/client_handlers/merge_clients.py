from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.commands import base_commands
from bot.routers.utility_commands.back import back
from bot.states.client import MergeClientsState
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
from database.queries.clients import find_client, get_client, merge_clients

router = Router()

commands = [
    "Отмена"
]


@router.message(StateFilter(None), F.text == "Связать клиентов")
async def add_client(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите клиента, который будет считаться головным",
        reply_markup=render_keyboard_buttons(commands, 2)
    )

    await state.set_state(MergeClientsState.choosing_main_client)


@router.message(StateFilter(MergeClientsState.choosing_main_client), F.text)
async def choosing_main_client_to_merge(message: Message, state: FSMContext):
    main_client_name = message.text
    if not await find_client(main_client_name):
        await message.answer(f"Клиента \"{main_client_name}\" не существует")
        return

    await state.update_data(main_client_name=main_client_name)
    await state.set_state(MergeClientsState.choosing_other_client)
    await message.answer("Выберите клиента, который будет считаться дочерним")


@router.message(StateFilter(MergeClientsState.choosing_other_client), F.text)
async def choosing_other_client_to_merge(message: Message, state: FSMContext):
    client_name = message.text
    client = await get_client(client_name)
    if not client:
        await message.answer(f"Клиента \"{client_name}\" не существует")
        return

    main_client_name = (await state.get_data()).get("main_client_name")
    if client.main_client_name:
        if client.main_client_name == main_client_name:
            await message.answer(f"Клиент \"{client_name}\" уже является дочерним к \"{main_client_name}\"")
        else:
            await message.answer(
                f"Клиент \"{client_name}\" уже является дочерним к другому клиенту \"{client.main_client_name}\""
            )
        return

    main_client = await get_client(main_client_name)
    if main_client.main_client_name == client_name:
        await message.answer(f"Ошибка! Клиент \"{main_client_name}\" является дочерним к \"{client_name}\"")
        return

    await state.update_data(other_client_name=client_name)
    await state.set_state(MergeClientsState.merge_client_confirmation)
    await message.answer(
        f"Клиент \"{client_name}\" будет привязан как дочерний к \"{main_client_name}\"",
        reply_markup=render_inline_buttons({"confirm_client_merge": "Подтвердить"}, 1)
    )


@router.callback_query(StateFilter(MergeClientsState.merge_client_confirmation), F.data == "confirm_client_merge")
async def confirm_client_merge(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        if not await merge_clients(data.get("main_client_name"), data.get("other_client_name")):
            raise Exception("Something went wrong")
        await query.answer("Клиенты успешно соединены")
    except Exception:
        await query.answer("Что-то пошло не так")

    if not await back(state):
        await query.message.answer(
            "Выберите действие",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )
