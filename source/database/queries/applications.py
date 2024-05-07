from sqlalchemy import insert, select, or_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.engine import async_session_factory
from database.models.application_orm import ApplicationORM
from database.models.other_orms import RelReasonApplicationORM
from schemas.contacts import Contact
from schemas.other import ApplicationReason
from schemas.applications import ApplicationAdd, Application, ApplicationFull

ApplicationFull.model_rebuild()


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


async def take_application(app_id: int, repairer_id: int) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            update(ApplicationORM)
            .where(ApplicationORM.id == app_id)
            .values(repairer_id=repairer_id)
            .returning(ApplicationORM.id)
        )

        app_id = (await session.execute(query)).scalar_one_or_none()

        await session.commit()
        return app_id is not None


async def search_applications(client_name_mask: str) -> list[Application]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM)
            .where(ApplicationORM.client_name.icontains(client_name_mask))
        )

        apps_orm = (await session.execute(query)).scalars().all()

        return [Application.model_validate(app, from_attributes=True) for app in apps_orm]


async def get_application(app_id: int) -> Application | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM)
            .where(ApplicationORM.id == app_id)
        )

        app_orm = (await session.execute(query)).scalar_one_or_none()

        return Application.model_validate(app_orm, from_attributes=True) if app_orm else None


async def get_applications(offset: int = 0, limit: int = 3, **params) -> list[ApplicationFull]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM)
            .options(selectinload(ApplicationORM.reasons), selectinload(ApplicationORM.contact))
            .offset(offset)
            .limit(limit)
        )

        if "client_name" in params:
            query = query.where(ApplicationORM.client_name == params["client_name"])
        if "worker_id" in params:
            query = query.where(
                or_(
                    ApplicationORM.repairer_id == params["worker_id"],
                    ApplicationORM.editor_id == params["worker_id"]
                )
            )

        apps_orm = (await session.execute(query)).scalars().all()

        return [ApplicationFull.model_validate(app, from_attributes=True) for app in apps_orm]
