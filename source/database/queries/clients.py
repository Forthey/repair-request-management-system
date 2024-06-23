from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from database.engine import async_session_factory

from database.models.client_orm import ClientORM

from database.queries.raw import Database

from schemas.clients import ClientAdd, Client


async def add_client(client: ClientAdd) -> str | None:
    return await Database.add(
        ClientORM, ClientORM.name, **client.model_dump()
    )


async def find_client(name: str) -> bool:
    return await Database.find(ClientORM, name=name)


async def search_clients(args: list[str]) -> list[Client]:
    return await Database.search(
        ClientORM, Client, {"name": ClientORM.name}, args, [ClientORM.name]
    )
