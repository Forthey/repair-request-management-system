from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import all_entity_strings
from schemas.addresses import Address
import database.queries.addresses as addr


router = Router()
router.inline_query.filter(
    InlineTargetFilter(all_entity_strings["address_strings"])
)


@router.inline_query()
async def search_clients_handler(inline_query: InlineQuery):
    address_name = " ".join(inline_query.query.split(" ")[1:])

    print(address_name)

    results: list[InlineQueryResultArticle] = []
    addresses: list[Address] = await addr.search_addresses(address_name)

    for address in addresses:
        results.append(InlineQueryResultArticle(
            id=address.name,
            title=f"{address.name}",
            description=f"{address.client_name}",
            input_message_content=InputTextMessageContent(
                message_text=address.name
            )
        ))

    await inline_query.answer(results, is_personal=True)
