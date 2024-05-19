from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import all_entity_strings
from schemas.contacts import Contact
import database.queries.contacts as con


router = Router()
router.inline_query.filter(
    InlineTargetFilter(all_entity_strings["contact_strings"])
)


@router.inline_query()
async def search_clients_handler(inline_query: InlineQuery):
    contact_args = inline_query.query.split(" ")[1:]

    contacts: list[Contact] = await con.search_contacts(contact_args)

    results: list[InlineQueryResultArticle] = []
    for contact in contacts:
        results.append(InlineQueryResultArticle(
            id=str(contact.id),
            title=f"{contact.surname} "
                  f"{contact.name if contact.name else ""} "
                  f"{contact.patronymic if contact.patronymic else ""}",
            description=f"{contact.client_name} - {contact.company_position}",
            input_message_content=InputTextMessageContent(
                message_text=str(contact.id)
            )
        ))

    await inline_query.answer(results, cache_time=3)
