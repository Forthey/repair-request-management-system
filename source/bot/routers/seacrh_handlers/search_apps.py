from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import app_strings
import database.queries.applications as app
from schemas.applications import Application

router = Router()
router.inline_query.filter(
    InlineTargetFilter(app_strings)
)


@router.inline_query()
async def search_apps(inline_query: InlineQuery):
    client = " ".join(inline_query.query.split(" ")[1:])

    results: list[InlineQueryResultArticle] = []
    apps: list[Application] = await app.search_applications(client)

    for application in apps:
        results.append(InlineQueryResultArticle(
            id=application.id.__str__(),
            title=f"{application.client_name} от {application.created_at.date()}",
            description=f"id: {application.id}, станок: {application.machine}",
            input_message_content=InputTextMessageContent(
                message_text=application.id.__str__()
            )
        ))

    await inline_query.answer(results, is_personal=True)
