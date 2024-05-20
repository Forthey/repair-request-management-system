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


async def search_clients(args: list[str]) -> list[Client]:
    session: AsyncSession
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(ClientORM)
                .order_by(ClientORM.name)
                .limit(50)
            )
            clients_orm = (await session.execute(query)).scalars().all()

            return [Client.model_validate(address, from_attributes=True) for address in clients_orm]

        query = (
            select(ClientORM)
            .where(ClientORM.name.icontains(args[0]))
            .order_by(ClientORM.name)
        )

        clients_orm = (await session.execute(query)).scalars().all()

        clients: list[Client] = []
        args = args[1:]
        for client in clients_orm:
            arg_not_matched = False
            for arg in args:
                if arg.lower() not in str(client.name).lower():
                    arg_not_matched = True
                    break
            if not arg_not_matched:
                clients.append(Client.model_validate(client, from_attributes=True))

        return clients
