import io

from sqlalchemy import insert, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory

from database.models.machine_orm import MachineORM

from database.queries.new import add_to_database
from database.queries.search import search_database

from schemas.machines import Machine

# from yandex_disk_storage.base import upload_file


async def add_machine(name: str, file_id: str | None = None) -> str | None:
    return await add_to_database(
        MachineORM, MachineORM.name, name=name, file_id=file_id
    )


async def find_machine(name: str) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(MachineORM)
            .where(MachineORM.name == name)
        )

        return (await session.execute(query)).scalar_one_or_none() is not None


async def search_machines(args: list[str]) -> list[Machine]:
    return await search_database(
        MachineORM, {"name": MachineORM.name}, args, Machine, MachineORM.name
    )
