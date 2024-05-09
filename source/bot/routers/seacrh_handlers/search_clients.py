from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import client_strings
from schemas.clients import Client
import database.queries.clients as c


router = Router()
router.inline_query.filter(
    InlineTargetFilter(client_strings)
)


@router.inline_query()
async def search_clients_handler(inline_query: InlineQuery):
    name = " ".join(inline_query.query.split(" ")[1:])

    results: list[InlineQueryResultArticle] = []
    clients: list[Client] = await c.search_clients(name)

    for client in clients:
        results.append(InlineQueryResultArticle(
            id=client.name,
            title=f"{client.name}",
            description=f"{client.activity}",
            input_message_content=InputTextMessageContent(
                message_text=client.name
            )
        ))

    await inline_query.answer(results, is_personal=True)