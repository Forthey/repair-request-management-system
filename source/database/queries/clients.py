from sqlalchemy import exists, select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from database.engine import async_session_factory
from database.models.client_orm import ClientORM
from schemas.clients import ClientAdd, Client


async def add_client(client: ClientAdd) -> str | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(ClientORM)
            .values(**client.model_dump())
            .returning(ClientORM.name)
        )

        try:
            name = (await session.execute(query)).scalar_one_or_none()

            await session.commit()
            return name
        except IntegrityError:
            return None


async def name_exists(name: str) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(count())
            .where(ClientORM.name == name)
        )

        return (await session.execute(query)).scalar_one() == 1


async def search_clients(mask: str) -> list[Client]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ClientORM)
            .where(ClientORM.name.icontains(mask))
        )

        clients_orm = (await session.execute(query)).scalars().all()

        return [Client.model_validate(client, from_attributes=True) for client in clients_orm]
