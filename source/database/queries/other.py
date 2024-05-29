from sqlalchemy import insert, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.other_orms import CompanyPositionORM, ApplicationReasonORM, CloseReasonORM, CompanyActivityORM
from database.queries.new import add_to_database
from database.queries.search import search_database
from schemas.other import ApplicationReason, CloseReason, CompanyActivity, CompanyPosition


async def add_company_position(position: str) -> str | None:
    return await add_to_database(
        CompanyPositionORM, CompanyActivityORM.name, name=position
    )


async def find_company_position(position: str) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(CompanyPositionORM)
            .where(CompanyPositionORM.name == position)
        )

        return (await session.execute(query)).scalar_one_or_none() is not None


async def search_company_position(args: list[str]) -> list[CompanyPosition]:
    return await search_database(
        CompanyPositionORM, {"name": CompanyPositionORM.name}, args, CompanyPosition, [CompanyPositionORM.name]
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
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationReasonORM)
            .where(
                and_(
                    ApplicationReasonORM.application_id == app_id,
                    ApplicationReasonORM.reason_name == reason
                )
            )
        )

        return (await session.execute(query)).scalar_one_or_none() is not None


async def add_close_reason(reason: str) -> str | None:
    return await add_to_database(
        CloseReasonORM, CloseReasonORM.name, name=reason
    )


async def search_close_reason(args: list[str]) -> list[CloseReason]:
    return await search_database(
        CloseReasonORM, {"name": CloseReasonORM.name}, args, CloseReason, [CloseReasonORM.name]
    )


async def find_close_reason(reason: str) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(CloseReasonORM)
            .where(CloseReasonORM.name == reason)
        )

        return (await session.execute(query)).scalar_one_or_none() is not None


async def add_company_activity(name: str) -> str | None:
    return await add_to_database(
        CompanyActivityORM, CompanyActivityORM.name, name=name
    )


async def search_company_activity(args: list[str]) -> list[CompanyActivity]:
    return await search_database(
        CompanyActivityORM, {"name": CompanyActivityORM.name}, args, CompanyActivity, [CompanyActivityORM.name]
    )
