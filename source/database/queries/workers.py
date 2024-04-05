from database.engine import async_session_factory, AsyncSession
from database.models.all import *
from schemas.workers import WorkerAdd, Worker


async def add_worker(worker: WorkerAdd):
    session: AsyncSession
    async with async_session_factory() as session:
        worker_orm = WorkerORM(**worker.model_dump())
        session.add(worker_orm)

        await session.commit()
