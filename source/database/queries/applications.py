from sqlalchemy import insert, select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.application_orm import ApplicationORM
from database.models.other_orms import RelReasonApplicationORM
from schemas.applications import ApplicationAdd, Application


async def add_application(application: ApplicationAdd, app_reasons: list[str]) -> int | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(ApplicationORM)
            .values(**application.model_dump())
            .returning(ApplicationORM.id)
        )

        try:
            app_id = (await session.execute(query)).scalar_one_or_none()

            for reason in app_reasons:
                session.add(RelReasonApplicationORM(application_id=app_id, reason_name=reason))

            await session.commit()
            return app_id
        except IntegrityError:
            return None


async def search_applications(client_name_mask: str) -> list[Application]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM)
            .where(ApplicationORM.client_name.icontains(client_name_mask))
        )

        apps_orm = (await session.execute(query)).scalars().all()

        return [Application.model_validate(app, from_attributes=True) for app in apps_orm]


async def get_applications_from_client(client_name: str, offset: int = 0) -> list[Application]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM)
            .where(ApplicationORM.client_name == client_name)
            .offset(offset)
            .limit(5)
        )

        apps_orm = (await session.execute(query)).scalars().all()

        return [Application.model_validate(app, from_attributes=True) for app in apps_orm]


async def get_applications_from_worker(worker_id: int, offset: int = 0) -> list[Application]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM)
            .where(
                or_(
                    ApplicationORM.repairer_id == worker_id,
                    ApplicationORM.editor_id == worker_id
                )
            )
            .offset(offset)
            .limit(5)
        )

        apps_orm = (await session.execute(query)).scalars().all()

        return [Application.model_validate(app, from_attributes=True) for app in apps_orm]
