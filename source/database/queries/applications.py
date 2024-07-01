import datetime

from sqlalchemy import insert, select, or_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import count

from database.engine import async_session_factory

from database.models.application_orm import ApplicationORM, ApplicationChangeLogORM
from database.models.other_orms import ApplicationReasonORM
from database.queries.raw import Database

from schemas.applications import ApplicationAdd, Application, ApplicationFull, ApplicationWithReasons, \
    ApplicationChangeLog

changeable_app_field_to_str = {
    "est_repair_date": "Примерная дата ремонта",
    "est_repair_duration_hours": "Примерная длительность ремонта",
    "client_name": "Клиент",
    "contact_id": "id Контакта",
    "address_name": "Адрес",
    "machine_name": "Станок",
    "notes": "Заметки"
}


async def count_worker_applications(telegram_id: int) -> int:
    async with async_session_factory() as session:
        query = (
            select(count())
            .select_from(ApplicationORM)
            .where(
                or_(
                    ApplicationORM.repairer_id == telegram_id,
                    ApplicationORM.editor_id == telegram_id
                )
            )
        )

        return (await session.execute(query)).scalar_one()


async def get_applications(offset: int = 0, limit: int = 3, **params) -> list[ApplicationWithReasons]:
    filters: dict = {}
    where_clause = or_()
    if "client_name" in params:
        filters["client_name"] = params["client_name"]
    if "worker_id" in params:
        where_clause = or_(
            ApplicationORM.repairer_id == params["worker_id"],
            ApplicationORM.editor_id == params["worker_id"]
        )

    return await Database.get(
        ApplicationORM, ApplicationWithReasons,
        [ApplicationORM.closed_at.desc(), ApplicationORM.created_at.desc()],
        offset, limit,
        [ApplicationORM.reasons],
        where_clause,
        **filters
    )


async def get_application(app_id: int) -> ApplicationFull | None:
    return await Database.get_one(
        ApplicationORM, ApplicationFull,
        [ApplicationORM.reasons, ApplicationORM.contact, ApplicationORM.machine, ApplicationORM.address],
        id=app_id
    )


async def search_applications(args: list[str]) -> list[Application]:
    return await Database.search(
        ApplicationORM, Application,
        {
            "client_name": ApplicationORM.client_name,
            "machine_name": ApplicationORM.machine_name,
            "address_name": ApplicationORM.address_name
        }, args,
        [ApplicationORM.closed_at.desc()],
    )


async def add_application(application: ApplicationAdd, app_reasons: list[str]) -> int | None:
    async with async_session_factory() as session:
        query = (
            insert(ApplicationORM)
            .values(**application.model_dump())
            .returning(ApplicationORM.id)
        )

        try:
            app_id = (await session.execute(query)).scalar_one_or_none()

            for reason in app_reasons:
                session.add(ApplicationReasonORM(application_id=app_id, reason_name=reason))

            await session.commit()
            return app_id
        except IntegrityError:
            return None


async def update_application(app_id: int, **fields):
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
    async with async_session_factory() as session:
        query = (
            update(ApplicationORM)
            .where(ApplicationORM.id == app_id)
            .values(repairer_id=repairer_id)
            .returning(ApplicationORM.id)
        )

        app_id = (await session.execute(query)).scalar_one_or_none()

        if app_id is None:
            return False

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
        return True


async def close_application(app_id: int, reason: str) -> bool:
    async with async_session_factory() as session:
        close_date = datetime.datetime.now(datetime.UTC)
        query = (
            update(ApplicationORM)
            .where(ApplicationORM.id == app_id)
            .values(
                close_reason=reason,
                closed_at=close_date
            )
            .returning(ApplicationORM.id)
        )

        app_id = (await session.execute(query)).scalar_one_or_none()

        if app_id is None:
            return False

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
        return True


async def add_application_log(app_id: int, field_name: str, old_value: str, new_value: str | None):
    await Database.add(ApplicationChangeLogORM,
                       application_id=app_id,
                       field_name=field_name,
                       old_value=old_value,
                       new_value=new_value)


async def get_application_logs(app_id: int) -> list[ApplicationChangeLog]:
    return await Database.get(ApplicationChangeLogORM, ApplicationChangeLog, application_id=app_id)
