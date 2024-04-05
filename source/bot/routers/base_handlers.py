from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup

from bot.utility.render_buttons import render_keyboard_buttons


base_commands = [
    "Добавить работника",
    "Добавить станок",
    "Добавить клиента",
    "Добавить адрес",
    "Добавить контакты",
    "Вывести подсказки"
]

router = Router()


@router.message(Command(commands=["start", "help"]))
@router.message(F.text.lower() == "вывести подсказки")
async def help(message: Message):
    buttons = render_keyboard_buttons(base_commands, 2)
    keyboard = ReplyKeyboardMarkup(keyboard=buttons)

    await message.answer(
        text="Выберите действие",
        reply_markup=keyboard
    )
