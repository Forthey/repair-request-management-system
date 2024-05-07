import io

from sqlalchemy import insert, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.machine_orm import MachineORM
from schemas.machines import Machine


async def add_machine(name: str, photo_url: str | None = None) -> bool:
    print(photo_url)
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(MachineORM)
            .values(
                name=name,
                photo_url=photo_url
            )
            .returning(MachineORM.name)
        )

        try:
            machine_name = (await session.execute(query)).scalar_one_or_none()
            await session.commit()
        except IntegrityError as e:
            return False
        return True


async def find_machine(name: str) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(MachineORM)
            .where(MachineORM.name == name)
        )

        return (await session.execute(query)).scalar_one_or_none() is not None


async def search_machines(name: str) -> list[Machine]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(MachineORM)
            .where(MachineORM.name.icontains(name))
        )

        machines_orm = (await session.execute(query)).scalars().all()

        return [Machine.model_validate(machine, from_attributes=True) for machine in machines_orm]
