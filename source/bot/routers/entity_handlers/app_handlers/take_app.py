from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.commands import base_commands
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
from bot.state_watchers.application import TakeApplicationState

from database.queries.applications import get_application, take_application
from schemas.applications import Application

router = Router()

commands = [
    "Отмена"
]


@router.message(StateFilter(None), F.text.lower() == "Взять заявку")
async def take_app(message: Message, state: FSMContext):
    await message.answer("Введите id заявки", reply_markup=render_keyboard_buttons(commands, 1))
    await state.set_state(TakeApplicationState.choosing_app_id)


@router.message(StateFilter(TakeApplicationState.choosing_app_id), F.text)
async def choosing_app_id(message: Message, state: FSMContext):
    try:
        app_id = int(message.text)
    except ValueError:
        await message.answer("Неправильный id")
        return

    app: Application | None = await get_application(app_id)

    if app is None:
        await message.answer("Заявки с таким id не существует")
        return
    if app.repairer_id is not None:
        await message.answer(f"Эта заявка уже взята")
        return

    await state.update_data(take_app_id=app_id)

    await message.answer(
        f"id = {app.id}\n"
        f"Заявка создана: {app.created_at.date()}\n"
        f"id Клиента: {app.client_name}\n"
        f"id Контакта: {app.contact_id}\n"
        f"Станок: {app.machine}\n"
        f"Адрес: {app.address}\n"
        f"Примерная дата ремонта: {
            app.est_repair_date.date() if app.est_repair_date is not None else "None"
        }\n"
        f"Примерное время ремонта: {app.est_repair_duration_hours}ч.\n"
        f"Взято в работу: {"Да" if app.repairer_id is not None else "Нет"}",
        reply_markup=render_inline_buttons({"confirm_take_app": "Взять заявку", "decline_take_app": "Выбрать другую"}, 1)
    )
    await state.set_state(TakeApplicationState.take_app_confirmation)


@router.callback_query(StateFilter(TakeApplicationState.take_app_confirmation), F.data == "decline_take_app")
async def decline_take_app(query: CallbackQuery, state: FSMContext):
    await state.set_state(TakeApplicationState.choosing_app_id)
    await query.answer("Отменено")
    await query.message.answer("Введите id заявки")


@router.callback_query(StateFilter(TakeApplicationState.take_app_confirmation), F.data == "confirm_take_app")
async def confirm_take_app(query: CallbackQuery, state: FSMContext):
    app_id = (await state.get_data()).get("take_app_id")

    if app_id is None or not await take_application(app_id, query.from_user.id):
        await query.answer("Что-то пошло не так...")
        return

    await query.answer(f"Заявка {app_id} взята Вами")
    await query.message.answer("Выберите действие", reply_markup=render_keyboard_buttons(base_commands, 2))
    await state.clear()

