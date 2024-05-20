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


async def search_company_position(args: list[str]) -> list[CompanyPosition]:
    session: AsyncSession
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(CompanyPositionORM)
                .order_by(CompanyPositionORM.name)
                .limit(50)
            )

            positions_orm = (await session.execute(query)).scalars().all()

            return [CompanyPosition.model_validate(position, from_attributes=True) for position in positions_orm]

        query = (
            select(CompanyPositionORM)
            .where(CompanyPositionORM.name.icontains(args[0]))
        )

        positions_orm = (await session.execute(query)).scalars().all()

        positions: list[CompanyPosition] = []
        args = args[1:]
        for position in positions_orm:
            arg_not_matched = False
            for arg in args:
                if arg.lower() not in str(position.name).lower():
                    arg_not_matched = True
                    break
            if not arg_not_matched:
                positions.append(CompanyPosition.model_validate(position, from_attributes=True))

        return positions


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


async def search_close_reason(args: list[str]) -> list[CloseReason]:
    session: AsyncSession
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(CloseReasonORM)
                .order_by(CloseReasonORM.name)
                .limit(50)
            )

            close_reasons_orm = (await session.execute(query)).scalars().all()

            return [CloseReason.model_validate(reason, from_attributes=True) for reason in close_reasons_orm]

        query = (
            select(CloseReasonORM)
            .where(CloseReasonORM.name.icontains(args[0]))
        )

        close_reasons_orm = (await session.execute(query)).scalars().all()

        close_reasons: list[CloseReason] = []
        args = args[1:]
        for close_reason in close_reasons_orm:
            arg_not_matched = False
            for arg in args:
                if arg.lower() not in str(close_reason.name).lower():
                    arg_not_matched = True
                    break
            if not arg_not_matched:
                close_reasons.append(CloseReason.model_validate(close_reason, from_attributes=True))

        return close_reasons


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
    session: AsyncSession
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(CompanyActivityORM)
                .order_by(CompanyActivityORM.name)
                .limit(50)
            )

            company_activities_orm = (await session.execute(query)).scalars().all()

            return [CompanyActivity.model_validate(activity, from_attributes=True) for activity in company_activities_orm]

        query = (
            select(CompanyActivityORM)
            .where(CompanyActivityORM.name.icontains(args[0]))
        )

        company_activities_orm = (await session.execute(query)).scalars().all()

        company_activities: list[CompanyActivity] = []
        args = args[1:]
        for company_activity in company_activities_orm:
            arg_not_matched = False
            for arg in args:
                if arg.lower() not in str(company_activity.name).lower():
                    arg_not_matched = True
                    break
            if not arg_not_matched:
                company_activities.append(CompanyActivity.model_validate(company_activity, from_attributes=True))

        return company_activities
