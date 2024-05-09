from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import contact_strings
from schemas.contacts import Contact
import database.queries.contacts as con


router = Router()
router.inline_query.filter(
    InlineTargetFilter(contact_strings)
)


@router.inline_query()
async def search_clients_handler(inline_query: InlineQuery):
    args = " ".join(inline_query.query.split(" ")[1:]).split(".")
    argc_len = len(args)

    client = args[0] if argc_len > 0 else ""
    surname = args[1] if argc_len > 1 else ""
    company_position = args[2] if argc_len > 2 else ""

    results: list[InlineQueryResultArticle] = []
    contacts: list[Contact] = await con.search_contacts(client, surname, company_position)

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

    await inline_query.answer(results, is_personal=True)