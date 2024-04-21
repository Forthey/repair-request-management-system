from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers import (
    seacrh_workers,
    search_machines,
    search_clients,
    search_contact,
    seacrh_address,
    search_other
)
from bot.target_names import all_strings

router = Router()


class InlineNonTargetFilter(BaseFilter):
    async def __call__(self, inline_query: InlineQuery) -> bool:
        args = inline_query.query.split(" ")
        return len(args) == 1 and (args[0].lower() not in all_strings)


@router.inline_query(InlineNonTargetFilter())
async def suggest_targets(inline_query: InlineQuery):
    results: list[InlineQueryResultArticle] = []
    target = inline_query.query.split(" ")[0]

    for string in all_strings:
        if target == " " or target in string:
            results.append(InlineQueryResultArticle(
                id=string,
                type="article",
                title=f"{string}",
                description=f"подсказка по сущностям",
                input_message_content=InputTextMessageContent(
                    message_text="$skip"
                )
            ))

    await inline_query.answer(results, is_personal=True)


router.include_routers(
    seacrh_workers.router,
    search_machines.router,
    search_clients.router,
    search_contact.router,
    seacrh_address.router,
    search_other.router
)
