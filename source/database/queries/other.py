from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.other_orms import CompanyPositionORM, ApplicationReasonORM, CloseReasonORM, CompanyActivityORM
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


async def search_company_position(mask: str) -> list[CompanyPosition]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(CompanyPositionORM)
            .where(CompanyPositionORM.name.icontains(mask))
        )

        positions_orm = (await session.execute(query)).scalars().all()

        return [CompanyPosition.model_validate(position, from_attributes=True) for position in positions_orm]


async def add_app_reason(reason: str) -> str | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(ApplicationReasonORM)
            .values(name=reason)
            .returning(ApplicationReasonORM.name)
        )

        try:
            reason = (await session.execute(query)).scalar_one_or_none()

            await session.commit()
            return reason
        except IntegrityError:
            return None


async def find_app_reason(reason: str) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationReasonORM)
            .where(ApplicationReasonORM.name == reason)
        )

        return (await session.execute(query)).scalar_one_or_none() is not None


async def search_app_reason(mask: str) -> list[ApplicationReason]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationReasonORM)
            .where(ApplicationReasonORM.name.icontains(mask))
        )

        reasons_orm = (await session.execute(query)).scalars().all()

        return [ApplicationReason.model_validate(reason, from_attributes=True) for reason in reasons_orm]


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


async def search_close_reason(mask: str) -> list[CloseReason]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(CloseReasonORM)
            .where(CloseReasonORM.name.icontains(mask))
        )

        reasons_orm = (await session.execute(query)).scalars().all()

        return [CloseReason.model_validate(reason, from_attributes=True) for reason in reasons_orm]


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


async def search_company_activity(mask: str) -> list[CompanyActivity]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(CompanyActivityORM)
            .where(CompanyActivityORM.name.icontains(mask))
        )

        activities_orm = (await session.execute(query)).scalars().all()

        return [CompanyActivity.model_validate(activity, from_attributes=True) for activity in activities_orm]
