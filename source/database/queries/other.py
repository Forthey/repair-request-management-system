from sqlalchemy import insert, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
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


async def add_company_activity(name: str) -> str | None:
    return await Database.add(
        CompanyActivityORM, CompanyActivityORM.name, name=name
    )


async def search_company_activity(args: list[str]) -> list[CompanyActivity]:
    return await Database.search(
        CompanyActivityORM, CompanyActivity, {"name": CompanyActivityORM.name}, args, [CompanyActivityORM.name]
    )
