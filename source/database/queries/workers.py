from sqlalchemy import select, update, delete, insert, or_, and_
from sqlalchemy.exc import IntegrityError

from database.engine import async_session_factory, AsyncSession

from database.models.application_orm import ApplicationORM
from database.models.worker_orm import WorkerORM
from database.queries.new import add_to_database
from database.queries.search import search_database

from schemas.workers import WorkerAdd, Worker


async def add_worker(worker: WorkerAdd) -> int | None:
    return await add_to_database(
        WorkerORM, WorkerORM.telegram_id, **worker.model_dump()
    )


async def get_workers() -> list[Worker]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(WorkerORM)
            .filter_by(active=True)
        )

        workers_orm = (await session.execute(query)).scalars().all()

        return [Worker.model_validate(worker, from_attributes=True) for worker in workers_orm]


async def search_workers(args: list[str]) -> list[Worker]:
    return await search_database(
        WorkerORM, {
            "surname": WorkerORM.surname,
            "name": WorkerORM.name,
            "patronymic": WorkerORM.patronymic,
            "access_right": WorkerORM.access_right
        }, args, Worker,
        [WorkerORM.surname, WorkerORM.name, WorkerORM.patronymic],
        active=True
    )


async def get_worker(telegram_id: int, force: bool = False) -> Worker | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(WorkerORM)
            .where(WorkerORM.telegram_id == telegram_id)
        )
        if not force:
            query = query.where(WorkerORM.active == True)

        worker_orm = (await session.execute(query)).scalars().one_or_none()
        result = Worker.model_validate(worker_orm, from_attributes=True) if worker_orm else None

        await session.commit()
        return result


async def update_worker(telegram_id, **worker_fields) -> Worker | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            update(WorkerORM)
            .where(WorkerORM.telegram_id == telegram_id)
            .values(**worker_fields)
            .returning(WorkerORM)
        )

        worker_orm = (await session.execute(query)).scalar_one_or_none()
        worker = Worker.model_validate(worker_orm, from_attributes=True) if worker_orm else None

        await session.commit()
        return worker
