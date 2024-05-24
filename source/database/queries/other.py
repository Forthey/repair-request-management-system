from sqlalchemy import insert, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.other_orms import CompanyPositionORM, ApplicationReasonORM, CloseReasonORM, CompanyActivityORM
from database.queries.search import search_database
from schemas.other import ApplicationReason, CloseReason, CompanyActivity, CompanyPosition


async def add_company_position(position: str) -> str | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(CompanyPositionORM)
            .values(name=position)
            .returning(CompanyPositionORM.name)
        )

        try:
            position = (await session.execute(query)).scalar_one_or_none()

            await session.commit()
            return position
        except IntegrityError:
            return None


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
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(CloseReasonORM)
            .values(name=reason)
            .returning(CloseReasonORM.name)
        )

        try:
            reason = (await session.execute(query)).scalar_one_or_none()

            await session.commit()
            return reason
        except IntegrityError:
            return None


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
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(CompanyActivityORM)
            .values(name=name)
            .returning(CompanyActivityORM.name)
        )

        try:
            activity = (await session.execute(query)).scalar_one_or_none()

            await session.commit()
            return activity
        except IntegrityError:
            return None


async def search_company_activity(args: list[str]) -> list[CompanyActivity]:
    return await search_database(
        CompanyActivityORM, {"name": CompanyActivityORM.name}, args, CompanyActivity, [CompanyActivityORM.name]
    )
