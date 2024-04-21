import io

from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, CallbackQuery, \
    InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.state_watchers.machine import MachineState

from bot.utility.render_buttons import render_keyboard_buttons, render_inline_buttons
from bot.commands import base_commands

from database.queries.machines import add_machine


router = Router()


commands = [
    "Отмена"
]


@router.message(StateFilter(None), F.text == "Добавить станок")
async def add_begin(message: Message, state: FSMContext):

    await message.answer(
        text=f"*Создание нового станка*",
        reply_markup=render_keyboard_buttons(commands, 2)
    )
    await message.answer(
        f"Введите _имя_ станка, а также его дату производства и другие данные\n"
        f"Также можно прикрепить фото, чтобы было удобней распознавать станок",
    )

    await state.set_state(MachineState.writing_machine_name)


@router.message(StateFilter(MachineState.writing_machine_name), F.photo)
async def add_name_with_photo(message: Message, state: FSMContext, bot: Bot):
    name = message.caption
    if len(name) < 3:
        await message.answer("Имя станка слишком короткое")
        return

    file_in_io = io.BytesIO()
    await bot.download(file=message.photo[-1], destination=file_in_io)
    if not await add_machine(name, file_in_io):
        await message.answer(
            text="Такой станок уже существует"
        )
        return
    else:
        await message.answer(
            text="Станок добавлен",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )

    await state.clear()


@router.message(StateFilter(MachineState.writing_machine_name), F.text)
async def add_name_without_photo(message: Message, state: FSMContext):
    name = message.text
    if len(name) < 3:
        await message.answer("Имя станка слишком короткое")
        return

    if not await add_machine(name):
        await message.answer("Такой станок уже существует")
        return
    else:
        await message.answer(
            text="Станок добавлен",
            reply_markup=render_keyboard_buttons(base_commands, 2)
        )

    await state.clear()
