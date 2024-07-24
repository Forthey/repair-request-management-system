from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states.address import AddressState


class MainFilter(BaseFilter):  # [1]
    def __init__(self):
        pass

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        if len(message.text) > 500:
            await message.answer("Сообщение слишком длинное")
            return False
        return True
