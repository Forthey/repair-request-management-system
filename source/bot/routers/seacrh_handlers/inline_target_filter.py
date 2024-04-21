from aiogram.filters import BaseFilter
from aiogram.types import InlineQuery


class InlineTargetFilter(BaseFilter):
    def __init__(self, target_strings: list[str]) -> None:
        self.target_strings = target_strings

    async def __call__(self, inline_query: InlineQuery) -> bool:  # [3]
        args = inline_query.query.split(" ")
        print(args)
        return args[0].lower() in self.target_strings
