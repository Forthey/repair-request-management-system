from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from bot.routers.seacrh_handlers.inline_target_filter import InlineTargetFilter
from bot.target_names import all_entity_strings
from schemas.other import ApplicationReason, CloseReason, CompanyActivity, CompanyPosition
import database.queries.other as o

router = Router()


@router.inline_query(InlineTargetFilter(all_entity_strings["app_reason_strings"]))
async def search_app_reasons(inline_query: InlineQuery):
    name = " ".join(inline_query.query.split(" ")[1:])

    results: list[InlineQueryResultArticle] = []
    machines: list[ApplicationReason] = await o.search_app_reason(name)

    for machine in machines:
        results.append(InlineQueryResultArticle(
            id=machine.name,
            title=f"{machine.name}",
            input_message_content=InputTextMessageContent(
                message_text=machine.name
            )
        ))

    await inline_query.answer(results, is_personal=True)


@router.inline_query(InlineTargetFilter(all_entity_strings["close_reason_strings"]))
async def search_close_reasons(inline_query: InlineQuery):
    name = " ".join(inline_query.query.split(" ")[1:])

    results: list[InlineQueryResultArticle] = []
    reasons: list[CloseReason] = await o.search_close_reason(name)

    for reason in reasons:
        results.append(InlineQueryResultArticle(
            id=reason.name,
            title=f"{reason.name}",
            input_message_content=InputTextMessageContent(
                message_text=reason.name
            )
        ))

    await inline_query.answer(results, is_personal=True)


@router.inline_query(InlineTargetFilter(all_entity_strings["company_activity_strings"]))
async def search_company_activity(inline_query: InlineQuery):
    name = " ".join(inline_query.query.split(" ")[1:])

    results: list[InlineQueryResultArticle] = []
    activities: list[CompanyActivity] = await o.search_company_activity(name)

    for activity in activities:
        results.append(InlineQueryResultArticle(
            id=activity.name,
            title=f"{activity.name}",
            input_message_content=InputTextMessageContent(
                message_text=activity.name
            )
        ))

    await inline_query.answer(results, is_personal=True)


@router.inline_query(InlineTargetFilter(all_entity_strings["company_position_strings"]))
async def search_company_position(inline_query: InlineQuery):
    name = " ".join(inline_query.query.split(" ")[1:])

    results: list[InlineQueryResultArticle] = []
    positions: list[CompanyPosition] = await o.search_company_position(name)

    for position in positions:
        results.append(InlineQueryResultArticle(
            id=position.name,
            title=f"{position.name}",
            input_message_content=InputTextMessageContent(
                message_text=position.name
            )
        ))

    await inline_query.answer(results, is_personal=True)
