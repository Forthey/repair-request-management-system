from sqlalchemy import select, update, delete, insert, or_, and_
from sqlalchemy.exc import IntegrityError

from database.engine import async_session_factory, AsyncSession

from database.models.application_orm import ApplicationORM
from database.models.worker_orm import WorkerORM

from schemas.workers import WorkerAdd, Worker


async def add_worker(worker: WorkerAdd) -> int | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(WorkerORM)
            .values(**worker.model_dump())
            .returning(WorkerORM.telegram_id)
        )

        try:
            worker_id = (await session.execute(query)).scalar_one()
            await session.commit()
            return worker_id
        except IntegrityError:
            return None


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
    session: AsyncSession
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(WorkerORM)
                .filter_by(active=True)
                .order_by(WorkerORM.surname, WorkerORM.name, WorkerORM.patronymic)
                .limit(50)
            )

            workers_orm = (await session.execute(query)).scalars().all()

            return [Worker.model_validate(worker_orm, from_attributes=True) for worker_orm in workers_orm]

        query = (
            select(WorkerORM)
            .filter_by(active=True)
            .where(
                or_(
                    WorkerORM.surname.icontains(args[0]),
                    WorkerORM.name.icontains(args[0]),
                    WorkerORM.patronymic.icontains(args[0]),
                    WorkerORM.access_right.icontains(args[0])
                )
            )
            .order_by(WorkerORM.surname, WorkerORM.name, WorkerORM.patronymic)
            .limit(50)
        )

        workers_orm = (await session.execute(query)).scalars().all()

        workers: list[Worker] = []
        args = args[1:]
        for worker in workers_orm:
            arg_not_matched = False
            for arg in args:
                if arg.lower() not in str(worker.surname).lower() and \
                        arg not in str(worker.name).lower() and \
                        arg not in str(worker.patronymic).lower() and \
                        arg not in str(worker.access_right).lower():
                    arg_not_matched = True
                    break
            if not arg_not_matched:
                workers.append(Worker.model_validate(worker, from_attributes=True))

        return workers


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
