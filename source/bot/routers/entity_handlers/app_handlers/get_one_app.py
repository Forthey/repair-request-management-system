from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder

from bot.commands import base_commands
from bot.utility.entities_to_str.app_to_str import full_app_to_str
from bot.utility.entities_to_str.logs_to_str import logs_to_str
from bot.utility.entities_to_str.worker_to_str import worker_to_str
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
from bot.states.application import ChooseOneApplicationState

from database.queries.applications import get_application, take_application, close_application, get_application_logs
from database.queries.other import find_close_reason
from database.queries.workers import get_worker
from schemas.applications import ApplicationFull

from redis_db.workers import check_admin_rights

router = Router()

commands = [
    "Отмена"
]

buttons = {
    "decline_take_app": "Выбрать другую",
    "show_app_logs": "Просмотреть историю изменений",
    "confirm_take_app": "Взять",
    "confirm_edit_app": "Изменить",
    "confirm_close_app": "Закрыть",
    "confirm_transfer_app": "Назначить рабочего",
}


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

    await state.update_data(app_id=app_id)

    active_buttons = {
        "decline_take_app": buttons["decline_take_app"],
        "show_app_logs": buttons["show_app_logs"]
    }
    if app.closed_at is None:
        if app.repairer_id is None:
            active_buttons["confirm_take_app"] = buttons["confirm_take_app"]
        active_buttons["confirm_edit_app"] = buttons["confirm_edit_app"]
        active_buttons["confirm_close_app"] = buttons["confirm_close_app"]

    if await check_admin_rights(message.from_user.id):
        active_buttons["confirm_transfer_app"] = buttons["confirm_transfer_app"]

    await message.answer(
        full_app_to_str(app),
        reply_markup=render_inline_buttons(active_buttons, 1),
    )

    if app.address is not None and app.address.photo_url is not None or \
            app.machine is not None and app.machine.photo_url is not None:
        album_builder = MediaGroupBuilder(
            caption="Фотографии, относящиеся к заявке"
        )
        if app.address.photo_url is not None:
            album_builder.add_photo(
                media=app.address.photo_url
            )
        if app.machine.photo_url is not None:
            album_builder.add_photo(
                media=app.machine.photo_url
            )
        await message.answer_media_group(
            media=album_builder.build()
        )
    await state.set_state(ChooseOneApplicationState.chosen_app_confirmation)


@router.callback_query(StateFilter(ChooseOneApplicationState.chosen_app_confirmation), F.data == "decline_take_app")
async def decline_take_app(query: CallbackQuery, state: FSMContext):
    await state.set_state(ChooseOneApplicationState.choosing_app_id)
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

    await query.message.answer("Опишите причину закрытия заявки")
    await state.set_state(ChooseOneApplicationState.writing_app_close_reason)


@router.message(StateFilter(ChooseOneApplicationState.writing_app_close_reason), F.text)
async def confirm_close_app(message: Message, state: FSMContext):
    close_reason: str = message.text

    if not await find_close_reason(close_reason):
        await message.answer("Такой причины не существует")
        return

    app_id = (await state.get_data()).get("app_id")

    if app_id is None or not await close_application(app_id, close_reason):
        await message.answer("Что-то пошло не так...")
        return

    await message.answer(f"Заявка {app_id} закрыта")
    await message.answer("Выберите действие", reply_markup=render_keyboard_buttons(base_commands, 2))
    await state.clear()


@router.callback_query(StateFilter(ChooseOneApplicationState.chosen_app_confirmation), F.data == "show_app_logs")
async def show_app_logs(query: CallbackQuery, state: FSMContext):
    app_id = (await state.get_data()).get("app_id")

    logs = await get_application_logs(app_id)

    await query.message.answer(logs_to_str(logs))


@router.callback_query(StateFilter(ChooseOneApplicationState.chosen_app_confirmation), F.data == "confirm_transfer_app")
async def confirm_transfer_app(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Введите id работника")

    await state.set_state(ChooseOneApplicationState.choosing_repairer_id)


@router.message(StateFilter(ChooseOneApplicationState.choosing_repairer_id), F.text)
async def transfer_app_to_repairer(message: Message, state: FSMContext):
    repairer_id = message.text
    try:
        repairer_id = int(repairer_id)
    except ValueError:
        await message.answer("Указан не id")
        return

    worker = await get_worker(repairer_id)
    if worker is None:
        await message.answer(f"Работника с id {repairer_id} не существует")
        return

    await state.update_data(repairer_id=repairer_id)
    await state.set_state(ChooseOneApplicationState.app_transfer_confirmation)
    await message.answer(
        "Заявка будет взята работником:\n"
        f"{worker_to_str(worker)}",
        reply_markup=render_inline_buttons({
            "do_confirm_app_transfer": "Подтвердить",
            "decline_app_transfer": "Выбрать другого"
        }, 1)
    )


@router.callback_query(StateFilter(ChooseOneApplicationState.app_transfer_confirmation),
                       F.data == "decline_app_transfer")
async def decline_app_transfer(query: CallbackQuery, state: FSMContext):
    await query.answer("Отменено")
    await query.message.answer("Введите id работника")
    await state.set_state(ChooseOneApplicationState.choosing_repairer_id)


@router.callback_query(StateFilter(ChooseOneApplicationState.app_transfer_confirmation),
                       F.data == "do_confirm_app_transfer")
async def do_confirm_app_transfer(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    app_id = data.get("app_id")
    repairer_id = data.get("repairer_id")

    if repairer_id is None or app_id is None or not await take_application(app_id, repairer_id):
        await query.answer("Что-то пошло не так...")
        return

    await query.answer("Заявка успешно передана")
    await state.clear()
    await query.message.answer(
        "Выберите действие",
        reply_markup=render_keyboard_buttons(base_commands, 2)
    )
