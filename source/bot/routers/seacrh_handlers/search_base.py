from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers import (
    search_apps,
    search_workers,
    search_machines,
    search_clients,
    search_contact,
    search_address,
    search_other
)
from bot.target_names import all_entity_strings

router = Router()


class InlineNonTargetFilter(BaseFilter):
    async def __call__(self, inline_query: InlineQuery) -> bool:
        args = inline_query.query.split(" ")
        for key, entity_string in all_entity_strings.items():
            if inline_query.query in entity_string:
                return False
        return len(args) == 1


@router.inline_query(InlineNonTargetFilter())
async def suggest_targets(inline_query: InlineQuery):
    results: list[InlineQueryResultArticle] = []
    target = inline_query.query.split(" ")[0]

    for key, entity_string in all_entity_strings.items():
        if target == " " or target in entity_string[0]:
            results.append(InlineQueryResultArticle(
                id=entity_string[0],
                type="article",
                title=f"{"/".join(entity_string)}",
                description=f"подсказка по сущностям, нажимать нет смысла",
                input_message_content=InputTextMessageContent(
                    message_text=f"/help search {entity_string}"
                )
            ))

    await inline_query.answer(results, cache_time=3)


router.include_routers(
    search_apps.router,
    search_workers.router,
    search_machines.router,
    search_clients.router,
    search_contact.router,
    search_address.router,
    search_other.router
)
