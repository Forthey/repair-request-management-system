from aiogram.filters import BaseFilter
from aiogram.types import Message


class TargetFilter(BaseFilter):
    def __init__(self, target_strings: list[str]) -> None:
        self.target_strings = target_strings

    async def __call__(self, message: Message) -> bool:  # [3]
        args = message.text.split(" ")[1:]
        if args[0].lower() in self.target_strings:
            return True
        await message.answer(f"Сущности {args[0]} не существует")
