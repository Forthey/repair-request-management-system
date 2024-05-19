from sqlalchemy import select, update, delete, insert, or_, and_
from sqlalchemy.exc import IntegrityError

from database.engine import async_session_factory, AsyncSession
from database.models.all import WorkerORM
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
        query = select(WorkerORM)

        workers_orm = (await session.execute(query)).scalars().all()

        return [Worker.model_validate(worker, from_attributes=True) for worker in workers_orm]


async def search_workers(args: list[str]) -> list[Worker]:
    session: AsyncSession
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(WorkerORM)
                .order_by(WorkerORM.surname)
                .order_by(WorkerORM.name)
                .order_by(WorkerORM.patronymic)
                .limit(50)
            )

            workers_orm = (await session.execute(query)).scalars().all()

            return [Worker.model_validate(worker_orm, from_attributes=True) for worker_orm in workers_orm]

        query = (
            select(WorkerORM)
            .where(
                or_(
                    WorkerORM.surname.icontains(args[0]),
                    WorkerORM.name.icontains(args[0]),
                    WorkerORM.patronymic.icontains(args[0]),
                    WorkerORM.access_right.icontains(args[0])
                )
            )
            .order_by(WorkerORM.surname)
            .order_by(WorkerORM.name)
            .order_by(WorkerORM.patronymic)
            .limit(50)
        )

        workers_orm = (await session.execute(query)).scalars().all()

        workers: list[Worker] = []
        for worker in workers_orm:
            for arg in args:
                if arg not in worker.surname and \
                        arg not in worker.name and \
                        arg not in str(worker.patronymic) and \
                        arg not in worker.access_right:
                    break

                workers.append(Worker.model_validate(worker, from_attributes=True))
                break

        return workers


async def get_worker(telegram_id: int) -> Worker | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(WorkerORM)
            .where(WorkerORM.telegram_id == telegram_id)
        )
        worker_orm = (await session.execute(query)).scalars().one_or_none()
        result = Worker.model_validate(worker_orm, from_attributes=True) if worker_orm else None

        await session.commit()
        return result


async def update_worker(telegram_id, **worker_fields):
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            update(WorkerORM)
            .where(WorkerORM.telegram_id == telegram_id)
            .values(**worker_fields)
        )

        await session.execute(query)
        await session.commit()


async def delete_worker(telegram_id: int) -> int | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            delete(WorkerORM)
            .where(WorkerORM.telegram_id == telegram_id)
            .returning(WorkerORM.telegram_id)
        )

        telegram_id: int | None = (await session.execute(query)).one_or_none()
        await session.commit()

        return telegram_id
