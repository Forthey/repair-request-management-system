from aiogram import Router, Bot
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import all_entity_strings
from schemas.machines import Machine
from database.queries.machines import search_machines


router = Router()
router.inline_query.filter(
    InlineTargetFilter(all_entity_strings["machine_strings"])
)


@router.inline_query()
async def search_machines_inline(inline_query: InlineQuery):
    machine_args = inline_query.query.split(" ")[1:]

    results: list[InlineQueryResultArticle] = []
    machines: list[Machine] = await search_machines(machine_args)

    for machine in machines:
        results.append(InlineQueryResultArticle(
            id=machine.name,
            title=f"{machine.name}",
            input_message_content=InputTextMessageContent(
                message_text=machine.name
            )
        ))

    await inline_query.answer(results, is_personal=True, cache_time=3)
