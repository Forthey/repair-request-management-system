from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.state_watchers.add_worker import AddWorkerState, AddWorkerFSM

from bot.utility.get_id_by_username import get_user_id
from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
from bot.routers.base_handlers import base_commands

from schemas.workers import WorkerAdd
from database.queries import workers

from bot.tmp_data import tmp_access_rights


router = Router()


commands = [
    "Далее",
    "Назад",
    "Отмена"
]


@router.message(F.text.lower() == "отмена")
async def cancel(message: Message, state: FSMContext):
    state_str = state.set_state()

    buttons = render_keyboard_buttons(base_commands, 2)
    if state_str is None:
        await state.set_data({})
        await message.answer(
            text="Нечего отменять",
            reply_markup=ReplyKeyboardMarkup(keyboard=buttons)
        )
        return

    await state.clear()
    await message.answer(
        text="Создание работника отменено",
        reply_markup=ReplyKeyboardMarkup(keyboard=buttons)
    )


@router.message(F.text.lower() == "далее")
async def skip_step(message: Message, state: FSMContext):
    await state.set_state(AddWorkerFSM.next(await state.get_state()))


@router.message(F.text.lower() == "назад")
async def skip_step(message: Message, state: FSMContext):
    await state.set_state(AddWorkerFSM.prev(await state.get_state()))


@router.message(StateFilter(None), F.text == "Добавить работника")
async def add_begin(message: Message, state: FSMContext):
    buttons = render_keyboard_buttons(commands, 2)

    await message.answer(
        text=f"*Создание нового работника*",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardMarkup(keyboard=buttons)
    )
    await message.answer(
        text=f"Введите _username_ работника в телеграме:",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(AddWorkerFSM.begin())


@router.message(StateFilter(AddWorkerState.writing_username), F.text)
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
        text=f"Введите _имя_ работника:",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(AddWorkerFSM.next(AddWorkerState.writing_username))


@router.message(StateFilter(AddWorkerState.writing_name), F.text)
async def add_name(message: Message, state: FSMContext):
    name: str = message.text

    if not name.isalpha():
        await message.answer(
            text=f"_Имя_ должно содежать только буквы",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await message.answer(
            text=f"Введите _имя_ работника:",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await state.update_data(name=name)

    await message.answer(
        text=f"Введите _фамилию_ работника:",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(AddWorkerFSM.next(AddWorkerState.writing_name))


@router.message(StateFilter(AddWorkerState.writing_surname), F.text)
async def add_surname(message: Message, state: FSMContext):
    surname: str = message.text

    if not surname.isalpha():
        await message.answer(
            text=f"_Фамилия_ должна содежать только буквы",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await message.answer(
            text=f"Введите _фамилию_ работника:",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await state.update_data(surname=surname)

    await message.answer(
        text=f"Введите _отчество_ работника:",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(AddWorkerFSM.next(AddWorkerState.writing_surname))


@router.message(StateFilter(AddWorkerState.writing_patronymic), F.text)
async def add_patronymic(message: Message, state: FSMContext):
    patronymic: str = message.text

    if not patronymic.isalpha():
        await message.answer(
            text=f"_Отчество_ должно содежать только буквы",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await message.answer(
            text=f"Введите _отчество_ работника:",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    await state.update_data(patronymic=patronymic)

    buttons = render_inline_buttons(tmp_access_rights, 2)

    builder = InlineKeyboardBuilder(buttons)

    await message.answer(
        text=f"Выберите _права_ _доступа_ для работника",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddWorkerFSM.next(AddWorkerState.writing_patronymic))


@router.callback_query(F.data.in_(tmp_access_rights))
async def add_access_rights(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() != AddWorkerState.choosing_access_rights.state:
        return

    access_right = callback.data

    await state.update_data(access_right=access_right)
    worker_data = await state.get_data()
    worker = WorkerAdd.model_validate(worker_data, from_attributes=True)

    builder = InlineKeyboardBuilder([[InlineKeyboardButton(
        text="Подтвердить",
        callback_data="Подтвердить"
    )]])

    await callback.message.answer(
        text=f"*Новый работник:*\n"
             f"id: {worker.telegram_id}\n"
             f"Имя: {worker.name}\n"
             f"Фамилия: {worker.surname}\n"
             f"Отчество: {worker.patronymic}\n"
             f"Права доступа: {worker.access_right}",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=builder.as_markup()
    )

    await state.set_state(AddWorkerFSM.next(AddWorkerState.choosing_access_rights))


@router.callback_query(F.data == "Подтвердить")
async def confirm_worker(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() != AddWorkerState.confirmation.state:
        return

    buttons = render_keyboard_buttons(base_commands, 2)
    keyboard = ReplyKeyboardMarkup(keyboard=buttons)

    worker_data = await state.get_data()
    worker = WorkerAdd.model_validate(worker_data, from_attributes=True)

    # await workers.add_worker(worker)

    await callback.answer(
        text=f"Работник добавлен"
    )

    await callback.message.answer(
        text="Выберите действие",
        reply_markup=keyboard
    )

    await state.clear()


@router.message(StateFilter(AddWorkerState.choosing_access_rights))
async def access_rights_chosen_incorrectly(message: Message, state: FSMContext):
    buttons = render_inline_buttons(tmp_access_rights, 2)

    builder = InlineKeyboardBuilder(buttons)

    await message.answer(
        text=f"Пожалуйста, выберите _права_ _доступа_",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=builder.as_markup()
    )
