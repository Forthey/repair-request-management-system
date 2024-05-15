from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import all_entity_strings
from schemas.workers import Worker
import database.queries.workers as w


router = Router()
router.inline_query.filter(
    InlineTargetFilter(all_entity_strings["worker_strings"])
)


@router.inline_query()
async def search_workers(inline_query: InlineQuery):
    args = inline_query.query.split(" ")[1:]
    name = args[0] if len(args) > 0 else ""
    surname = args[1] if len(args) > 1 else ""
    patronymic = args[2] if len(args) > 2 else None

    results: list[InlineQueryResultArticle] = []
    workers: list[Worker] = await w.search_workers(name, surname, patronymic)

    for worker in workers:
        results.append(InlineQueryResultArticle(
            id=worker.telegram_id.__str__(),
            title=f"{worker.name} {worker.surname}",
            description=f"id в Телеграме: {worker.telegram_id}",
            input_message_content=InputTextMessageContent(
                message_text=worker.telegram_id.__str__()
            )
        ))

    await inline_query.answer(results, is_personal=True, cache_time=3)
