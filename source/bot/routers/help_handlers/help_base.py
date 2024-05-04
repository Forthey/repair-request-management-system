from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
router.message.filter(Command("help"))

with open("../md/help/help.md", "r", encoding="utf-8") as file:
    help_text = file.read()


@router.message()
async def print_help(message: Message):
    await message.answer(help_text, parse_mode="MARKDOWNV2")
