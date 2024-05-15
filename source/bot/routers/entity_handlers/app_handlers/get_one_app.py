from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.commands import base_commands
from bot.utility.entities_to_str.app_to_str import full_app_to_str
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
from bot.states.application import ChooseOneApplicationState

from database.queries.applications import get_application, take_application, close_application
from database.queries.other import find_close_reason
from schemas.applications import ApplicationFull

router = Router()

commands = [
    "Отмена"
]


@router.message(StateFilter(None), F.text.lower() == "выбрать заявку")
async def take_app(message: Message, state: FSMContext):
    await message.answer("Введите id заявки", reply_markup=render_keyboard_buttons(commands, 1))
    await state.set_state(ChooseOneApplicationState.choosing_app_id)


@router.message(StateFilter(ChooseOneApplicationState.choosing_app_id), F.text)
async def choosing_app_id(message: Message, state: FSMContext):
    try:
        app_id = int(message.text)
    except ValueError:
        await message.answer("Неправильный id")
        return

    app: ApplicationFull | None = await get_application(app_id)

    if app is None:
        await message.answer("Заявки с таким id не существует")
        return
    if app.repairer_id is not None:
        await message.answer(f"Эта заявка уже взята")
        return

    await state.update_data(app_id=app_id)

    buttons = {
        "decline_take_app": "Выбрать другую",
    }
    if app.closed_at is None:
        buttons["confirm_take_app"] = "Взять"
        buttons["confirm_edit_app"] = "Изменить"
        buttons["confirm_close_app"] = "Закрыть"

    await message.answer(
        full_app_to_str(app),
        reply_markup=render_inline_buttons(buttons, 1),
    )
    if app.address.photo_url is not None:
        await message.reply_photo(app.address.photo_url)
    if app.machine.photo_url is not None:
        await message.reply_photo(app.machine.photo_url)
    await state.set_state(ChooseOneApplicationState.chosen_app_confirmation)


@router.callback_query(StateFilter(ChooseOneApplicationState.chosen_app_confirmation), F.data == "decline_take_app")
async def decline_take_app(query: CallbackQuery, state: FSMContext):
    await state.set_state(ChooseOneApplicationState.chosen_app_confirmation)
    await query.answer("Отменено")
    await query.message.answer("Введите id заявки")


@router.callback_query(StateFilter(ChooseOneApplicationState.chosen_app_confirmation), F.data == "confirm_take_app")
async def confirm_take_app(query: CallbackQuery, state: FSMContext):
    app_id = (await state.get_data()).get("app_id")

    if app_id is None or not await take_application(app_id, query.from_user.id):
        await query.answer("Что-то пошло не так...")
        return

    await query.answer(f"Заявка {app_id} взята Вами")
    await query.message.answer("Выберите действие", reply_markup=render_keyboard_buttons(base_commands, 2))
    await state.clear()


@router.callback_query(StateFilter(ChooseOneApplicationState.chosen_app_confirmation), F.data == "confirm_close_app")
async def writing_close_app_reason(query: CallbackQuery, state: FSMContext):
    app_id = (await state.get_data()).get("app_id")
    if app_id is None:
        await query.answer("Что-то пошло не так...")

    await query.message.answer(
        "Опишите причину закрытия заявки",
        reply_markup=render_inline_buttons({"skip_close_reason_add": "Пропустить"}, 1)
    )
    await state.set_state(ChooseOneApplicationState.writing_app_close_reason)


@router.message(StateFilter(ChooseOneApplicationState.writing_app_close_reason), F.text)
async def confirm_close_app(message: Message, state: FSMContext):
    close_reason: str = message.text

    if not find_close_reason(close_reason):
        await message.answer("Такой причины не существует")
        return

    app_id = (await state.get_data()).get("app_id")

    if app_id is None or not await close_application(app_id, close_reason):
        await message.answer("Что-то пошло не так...")
        return

    await message.answer(f"Заявка {app_id} закрыта")
    await message.answer("Выберите действие", reply_markup=render_keyboard_buttons(base_commands, 2))
    await state.clear()
