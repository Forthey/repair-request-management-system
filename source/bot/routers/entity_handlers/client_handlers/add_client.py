from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from pydantic import ValidationError

from bot.commands import base_commands
from bot.routers.utility_commands.back import back
from bot.states.client import ClientState
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
import database.queries.clients as db_clients
import database.queries.other as db_other
from schemas.clients import Client, ClientAdd

router = Router()

commands = [
    "Далее",
    "Назад",
    "Отмена"
]


@router.message(StateFilter(None), F.text.lower() == "добавить клиента")
async def add_client(message: Message, state: FSMContext):
    await message.answer(
        text="Создание нового клиента (компании)",
        reply_markup=render_keyboard_buttons(commands, 2)
    )
    await message.answer(
        text="Введите название клиента (компании):"
    )

    await state.set_state(ClientState.writing_client_name)


@router.message(StateFilter(ClientState.writing_client_name), F.text)
async def add_client_name(message: Message, state: FSMContext):
    if message.text == "Далее":
        client_data = await state.get_data()
        if client_data.get("name") is None:
            await message.answer(
                text="Это поле пропустить нельзя"
            )
            return
        else:
            await state.set_state(ClientState.choosing_main_client)
            await message.answer("Выберите головную компанию")
            return

    if message.text == "Назад":
        await message.answer("Это первое поле")
        return

    name = message.text
    if await db_clients.find_client(name):
        await message.answer("Такой клиент уже существует")
        return

    await message.answer("Выберите головную компанию")

    await state.update_data(name=name)
    await state.set_state(ClientState.choosing_main_client)


@router.message(StateFilter(ClientState.choosing_main_client), F.text)
async def choose_main_client(message: Message, state: FSMContext):
    if message.text == "Далее":
        await message.answer("Выберите направление деятельности клиента")
        await state.set_state(ClientState.choosing_activity)
        return
    if message.text == "Назад":
        await message.answer("Введите название клиента (компании)")
        await state.set_state(ClientState.writing_client_name)
        return

    main_client_name = message.text
    if not db_clients.find_client(main_client_name):
        await message.answer("Такого клиента не существует")
        return

    await message.answer("Выберите направление деятельности клиента")

    await state.update_data(main_client_name=main_client_name)
    await state.set_state(ClientState.choosing_activity)


@router.message(StateFilter(ClientState.choosing_activity), F.text)
async def choose_activity(message: Message, state: FSMContext):
    if message.text == "Назад":
        await message.answer("Выберите головную компанию")
        await state.set_state(ClientState.choosing_main_client)
        return

    if message.text != "Далее":
        activity = message.text
        if len(await db_other.search_company_activity(activity)) != 1:
            await message.answer("Такого направления деятельности не существует")
            return
        await state.update_data(activity=message.text)

    client_data = await state.get_data()

    try:
        client = ClientAdd.model_validate(client_data, from_attributes=True)
    except ValidationError as e:
        await message.answer("Есть незаполненные обязательные поля")
        return

    await message.answer(
        f"Имя компании: {client.name}\n"
        f"Головная компания: {client.main_client_name}\n"
        f"Деятельность: {client.activity}\n",
        reply_markup=render_inline_buttons({"confirm_client_add": "Подтвердить", "cancel_client_add": "Отмена"}, 1)
    )

    await state.set_state(ClientState.add_client_confirmation)


@router.callback_query(StateFilter(ClientState.add_client_confirmation), F.data == "cancel_client_add")
async def add_app_confirmation_cancel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer("Отменено")
    await state.set_state(ClientState.choosing_activity)
    # await callback_query.message.answer(states_strings[ClientState.choosing_activity])
    # TODO: states_strings


@router.callback_query(StateFilter(ClientState.add_client_confirmation), F.data == "confirm_client_add")
async def add_client_confirmation(callback: CallbackQuery, state: FSMContext):
    client_data = await state.get_data()
    client = ClientAdd.model_validate(client_data, from_attributes=True)

    await db_clients.add_client(client)

    await callback.answer("Клиент добавлен")
    if not await back(state):
        await callback.message.answer(
            "Выберите действие",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )

