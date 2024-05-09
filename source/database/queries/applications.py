import datetime

from sqlalchemy import insert, select, or_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.engine import async_session_factory
from database.models.application_orm import ApplicationORM, ApplicationChangeLogORM
from database.models.other_orms import RelReasonApplicationORM
from schemas.contacts import Contact
from schemas.other import ApplicationReason
from schemas.applications import ApplicationAdd, Application, ApplicationFull

ApplicationFull.model_rebuild()


changeable_app_field_to_str = {
    "est_repair_date": "Примерная дата ремонта",
    "est_repair_duration_hours": "Примерная длительность ремонта",
    "client_name": "Клиент",
    "contact_id": "id Контакта",
    "address": "Адрес",
    "machine": "Станок",
    "notes": "Заметки"
}


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


async def get_application(app_id: int) -> Application | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM)
            .where(ApplicationORM.id == app_id)
        )

        app_orm = (await session.execute(query)).scalar_one_or_none()

        return Application.model_validate(app_orm, from_attributes=True) if app_orm else None


async def search_applications(client_name_mask: str) -> list[Application]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM)
            .where(ApplicationORM.client_name.icontains(client_name_mask))
        )

        apps_orm = (await session.execute(query)).scalars().all()

        return [Application.model_validate(app, from_attributes=True) for app in apps_orm]


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


async def update_application(app_id: int, **fields):
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM)
            .where(ApplicationORM.id == app_id)
        )

        app = (await session.execute(query)).scalar_one()

        for key in fields:
            session.add(ApplicationChangeLogORM(
                application_id=app_id,
                field_name=changeable_app_field_to_str[key],
                old_value=getattr(app, key),
                new_value=fields[key]
            ))

        query = (
            update(ApplicationORM)
            .where(ApplicationORM.id == app_id)
            .values(**fields)

        )

        await session.execute(query)

        await session.commit()


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

        log_query = (
            insert(ApplicationChangeLogORM)
            .values(
                application_id=app_id,
                field_name="Заявка взята на ремонт",
                old_value=None,
                new_value=repairer_id
            )
        )
        await session.execute(log_query)

        await session.commit()
        return app_id is not None


async def close_application(app_id: int, reason: str):
    session: AsyncSession
    async with async_session_factory() as session:
        close_date = datetime.datetime.now(datetime.UTC)
        query = (
            update(ApplicationORM)
            .where(ApplicationORM.id == app_id)
            .values(
                close_reason=reason,
                closed_at=close_date
            )
        )

        await session.execute(query)

        log_query = (
            insert(ApplicationChangeLogORM)
            .values(
                application_id=app_id,
                field_name="Заявка закрыта",
                old_value=None,
                new_value=close_date
            )
        )

        await session.execute(log_query)

        await session.commit()


async def add_application_log(app_id: int, field_name: str, old_value: str, new_value: str | None):
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(ApplicationChangeLogORM)
            .values(
                application_id=app_id,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value
            )
        )

        await session.execute(query)

        await session.commit()
