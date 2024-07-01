from sqlalchemy import insert, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.application_orm import ApplicationORM
from database.models.client_orm import ClientORM
from database.models.contact_orm import ContactORM
from database.models.other_orms import CompanyPositionORM, ApplicationReasonORM, CloseReasonORM, CompanyActivityORM

from database.queries.raw import Database

from schemas.other import CloseReason, CompanyActivity, CompanyPosition


async def add_company_position(position: str) -> str | None:
    return await Database.add(
        CompanyPositionORM, CompanyPositionORM.name, name=position
    )


async def find_company_position(position: str) -> bool:
    return await Database.find(CompanyPositionORM, name=position)


async def search_company_position(args: list[str]) -> list[CompanyPosition]:
    return await Database.search(
        CompanyPositionORM, CompanyPosition, {"name": CompanyPositionORM.name}, args, [CompanyPositionORM.name]
    )


async def check_if_company_position_safe_to_delete(position: str) -> bool:
    return await Database.check_if_safe_to_delete(
        position,
        ContactORM.company_position,
    )


async def delete_company_position(position: str) -> str:
    return await Database.delete(CompanyPositionORM, CompanyPositionORM.name, position)


async def add_app_reason(app_id: int, reason: str) -> str | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(ApplicationReasonORM)
            .values(
                application_id=app_id,
                reason_name=reason
            )
            .returning(ApplicationReasonORM.reason_name)
        )

        try:
            reason = (await session.execute(query)).scalar_one_or_none()

            await session.commit()
            return reason
        except IntegrityError:
            return None


async def find_app_reason(app_id: int, reason: str) -> bool:
    return await Database.find(ApplicationReasonORM, application_id=app_id, reason_name=reason)


async def add_close_reason(reason: str) -> str | None:
    return await Database.add(
        CloseReasonORM, CloseReasonORM.name, name=reason
    )


async def search_close_reason(args: list[str]) -> list[CloseReason]:
    return await Database.search(
        CloseReasonORM, CloseReason, {"name": CloseReasonORM.name}, args, [CloseReasonORM.name]
    )


async def find_close_reason(reason: str) -> bool:
    return await Database.find(CloseReasonORM, name=reason)


async def check_if_close_reason_safe_to_delete(reason: str) -> bool:
    return await Database.check_if_safe_to_delete(
        reason,
        ApplicationORM.close_reason,
    )


async def delete_close_reason(reason: str) -> str:
    return await Database.delete(CloseReasonORM, CloseReasonORM.name, reason)


async def add_company_activity(activity: str) -> str | None:
    return await Database.add(
        CompanyActivityORM, CompanyActivityORM.name, name=activity
    )


async def search_company_activity(args: list[str]) -> list[CompanyActivity]:
    return await Database.search(
        CompanyActivityORM, CompanyActivity, {"name": CompanyActivityORM.name}, args, [CompanyActivityORM.name]
    )


async def check_if_company_activity_safe_to_delete(activity: str) -> bool:
    return await Database.check_if_safe_to_delete(
        activity,
        ClientORM.activity,
    )


async def delete_company_activity(activity: str) -> str:
    return await Database.delete(CompanyActivityORM, CompanyActivityORM.name, activity)
