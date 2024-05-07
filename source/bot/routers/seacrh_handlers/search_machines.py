from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import machine_strings
from schemas.machines import Machine
from database.queries.machines import search_machines

router = Router()
router.inline_query.filter(
    InlineTargetFilter(machine_strings)
)


@router.inline_query()
async def search_workers(inline_query: InlineQuery):
    name = " ".join(inline_query.query.split(" ")[1:])

    results: list[InlineQueryResultArticle] = []
    machines: list[Machine] = await search_machines(name)

    for machine in machines:
        results.append(InlineQueryResultArticle(
            id=machine.name,
            title=f"{machine.name}",
            input_message_content=InputTextMessageContent(
                message_text=machine.name
            ),
            thumbnail_url="https://reiner-cnc.ru/upload/iblock/420/_0018_ER-00013929.jpg.jpg"
        ))

    await inline_query.answer(results, is_personal=True)
