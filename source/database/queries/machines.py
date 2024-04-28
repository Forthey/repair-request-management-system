import io

from sqlalchemy import insert, update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.machine_orm import MachineORM
from schemas.machines import Machine


async def add_machine(name: str, photo: io.BytesIO | None = None) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(MachineORM)
            .values(
                name=name
            )
            .returning(MachineORM.name)
        )

        try:
            machine_name = (await session.execute(query)).scalar_one_or_none()

            if photo is None:
                await session.commit()
                return True

            photo_url: str = f"./images/machine_{machine_name}.jpg"
            with open(photo_url, "wb") as f:
                f.write(photo.read())

            query = (
                update(MachineORM)
                .where(MachineORM.name == machine_name)
                .values(photo_url=photo_url)
            )

            await session.execute(query)
            await session.commit()

            return True
        except IntegrityError as e:
            print(e)
            return False


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
