from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.states.worker import WorkerState

from bot.utility.get_id_by_username import get_user_id
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
from bot.commands import base_commands
from redis_db.workers import reload_worker

from schemas.workers import WorkerAdd
from database.queries import workers as w

from bot.target_names import access_rights


router = Router()


commands = [
    "Отмена"
]


@router.message(StateFilter(None), F.text.lower() == "добавить работника")
async def add_begin(message: Message, state: FSMContext):
    await message.answer(
        text=f"*Создание нового работника*",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=render_keyboard_buttons(commands, 2)
    )
    await message.answer(
        text=f"Введите _username_ работника в телеграме:",
        parse_mode=ParseMode.MARKDOWN_V2
    )

    await state.set_state(WorkerState.writing_worker_username)


@router.message(StateFilter(WorkerState.writing_worker_username), F.text)
async def add_username(message: Message, state: FSMContext):
    username = message.text
    if "@" not in username:
        username = "@" + username

    user_id = await get_user_id(username)

    if user_id is None:
        await message.answer(
            text=f"Пользователя с _username_ *{username}* не существует 😕",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await message.answer(
            text=f"Введите _username_ работника в телеграме:",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await message.answer(
        text=f"_username_ — *{username}*\n"
             f"_id_ — *{user_id}*",
        parse_mode=ParseMode.MARKDOWN_V2
    )

    await state.update_data(telegram_id=user_id)

    await message.answer(
        text=f"Введите ФИО работника через пробел\n"
             f"Например: Зубенко Михаил Петрович\n"
             f"Отчество можно не указывать",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(WorkerState.writing_worker_fio)


@router.message(StateFilter(WorkerState.writing_worker_fio), F.text)
async def add_name(message: Message, state: FSMContext):
    fio: list[str] = message.text.split(" ")
    problems_occurred = False

    if len(fio) > 3 or len(fio) < 2:
        await message.answer(
            text=f"Кажется, вы ввели меньше или больше, чем нужно\n"
                 f"Попробуйте ещё раз",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        problems_occurred = True

    for word in fio:
        if not word.isalpha():
            await message.answer(
                text=f"ФИО должно содежать только буквы английского и русского алфавитов\n"
                     f"Попробуйте ещё раз",
                parse_mode=ParseMode.MARKDOWN_V2
            )

    if problems_occurred:
        await message.answer(
            text=f"Введите ФИО работника через пробел\n"
                 f"Например: Зубенко Михаил Петрович\n"
                 f"Отчество можно не указывать",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await state.update_data(
        surname=fio[0],
        name=fio[1],
        patronymic=(fio[2] if len(fio) == 3 else None)
    )

    await message.answer(
        text=f"Выберите _права_ _доступа_ для работника",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=render_inline_buttons(access_rights, 2)
    )
    await state.set_state(WorkerState.choosing_worker_access_rights)


@router.callback_query(StateFilter(WorkerState.choosing_worker_access_rights), F.data.in_(access_rights))
async def add_access_rights(callback: CallbackQuery, state: FSMContext):
    access_right = callback.data

    await state.update_data(access_right=access_right)
    worker_data = await state.get_data()
    worker = WorkerAdd.model_validate(worker_data, from_attributes=True)

    await callback.message.answer(
        text=f"*Новый работник:*\n"
             f"id: {worker.telegram_id}\n"
             f"Имя: {worker.name}\n"
             f"Фамилия: {worker.surname}\n"
             f"Отчество: {worker.patronymic}\n"
             f"Права доступа: {worker.access_right}",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=render_inline_buttons({"confirm_worker_add": "Подтвердить"}, 1)
    )

    await state.set_state(WorkerState.add_worker_confirmation)


@router.callback_query(StateFilter(WorkerState.add_worker_confirmation), F.data == "confirm_worker_add")
async def confirm_worker(callback: CallbackQuery, state: FSMContext):
    worker_data = await state.get_data()
    worker = WorkerAdd.model_validate(worker_data, from_attributes=True)

    if not await w.add_worker(worker):
        await callback.message.answer(
            text="Работник с таким именем уже существует",
        )
        await state.set_state(WorkerState.choosing_worker_access_rights)
        return

    await callback.answer(
        text=f"Работник добавлен"
    )

    await reload_worker(worker.telegram_id)

    await callback.message.answer(
        text="Выберите действие",
        reply_markup=render_keyboard_buttons(base_commands, 2)
    )

    await state.clear()


@router.message(StateFilter(WorkerState.choosing_worker_access_rights))
async def access_rights_chosen_incorrectly(message: Message, state: FSMContext):
    await message.answer(
        text=f"Пожалуйста, выберите права доступа",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=render_inline_buttons(access_rights, 2)
    )
