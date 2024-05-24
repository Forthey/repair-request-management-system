import io

from sqlalchemy import insert, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.machine_orm import MachineORM
from schemas.machines import Machine

# from yandex_disk_storage.base import upload_file


async def add_machine(name: str, file_id: str | None = None) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(MachineORM)
            .values(
                name=name,
                photo_url=file_id
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


async def search_machines(args: list[str]) -> list[Machine]:
    session: AsyncSession
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(MachineORM)
                .order_by(MachineORM.name)
                .limit(50)
            )
            machines_orm = (await session.execute(query)).scalars().all()

            return [Machine.model_validate(address, from_attributes=True) for address in machines_orm]

        query = (
            select(MachineORM)
            .where(MachineORM.name.icontains(args[0]))
            .order_by(MachineORM.name)
        )

        machines_orm = (await session.execute(query)).scalars().all()

        machines: list[Machine] = []
        args = args[1:]
        for machine in machines_orm:
            arg_not_matched = False
            for arg in args:
                if arg.lower() not in str(machine.name).lower():
                    arg_not_matched = True
                    break
            if not arg_not_matched:
                machines.append(Machine.model_validate(machine, from_attributes=True))

        return machines
