from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import all_entity_strings
from redis_db.workers import check_admin_rights
from schemas.workers import Worker
import database.queries.workers as w


router = Router()
router.inline_query.filter(
    InlineTargetFilter(all_entity_strings["worker_strings"])
)


@router.inline_query()
async def search_workers(inline_query: InlineQuery):
    if not await check_admin_rights(inline_query.from_user.id):
        return

    worker_args = inline_query.query.split(" ")[1:]

    results: list[InlineQueryResultArticle] = []
    workers: list[Worker] = await w.search_workers(worker_args)

    for worker in workers:
        results.append(InlineQueryResultArticle(
            id=worker.telegram_id.__str__(),
            title=f"{worker.name} {worker.surname} {worker.patronymic if worker.patronymic else ""}",
            description=f"id в Телеграме: {worker.telegram_id}; \n"
                        f"{worker.access_right}",
            input_message_content=InputTextMessageContent(
                message_text=worker.telegram_id.__str__()
            )
        ))

    await inline_query.answer(results, is_personal=True, cache_time=3)
