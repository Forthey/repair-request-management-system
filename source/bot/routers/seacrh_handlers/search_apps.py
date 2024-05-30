from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import all_entity_strings
import database.queries.applications as app
from bot.utility.pretty_date import date_to_str
from schemas.applications import Application

router = Router()
router.inline_query.filter(
    InlineTargetFilter(all_entity_strings["app_strings"])
)


@router.inline_query()
async def search_apps(inline_query: InlineQuery):
    app_args = inline_query.query.split(" ")[1:]

    results: list[InlineQueryResultArticle] = []
    apps: list[Application] = await app.search_applications(app_args)

    for application in apps:
        results.append(InlineQueryResultArticle(
            id=application.id.__str__(),
            title=f"'{application.client_name}' ({date_to_str(application.created_at)})",
            description=f"id: {application.id}; \n"
                        f"Станок: {application.machine_name if application.machine_name else "Не указан"}; \n"
                        f"Адрес: {application.address_name if application.address_name else "Не указан"}",
            input_message_content=InputTextMessageContent(
                message_text=application.id.__str__()
            )
        ))

    await inline_query.answer(results, is_personal=True, cache_time=3)
