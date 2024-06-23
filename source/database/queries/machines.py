from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory

from database.models.machine_orm import MachineORM

from database.queries.raw import Database

from schemas.machines import Machine

# from yandex_disk_storage.base import upload_file


async def add_machine(name: str, file_id: str | None = None) -> str | None:
    return await Database.add(
        MachineORM, MachineORM.name, name=name, photo_url=file_id
    )


async def find_machine(name: str) -> bool:
    return await Database.find(MachineORM, name=name)


async def get_machine(name: str) -> Machine | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(MachineORM)
            .where(MachineORM.name == name)
        )

        machine_orm = (await session.execute(query)).scalar_one_or_none()

        return Machine.model_validate(machine_orm, from_attributes=True) if machine_orm else None


async def search_machines(args: list[str]) -> list[Machine]:
    return await Database.search(
        MachineORM, Machine, {"name": MachineORM.name}, args, [MachineORM.name]
    )
