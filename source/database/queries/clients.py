from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from database.engine import async_session_factory
from database.models.address_orm import AddressORM
from database.models.application_orm import ApplicationORM

from database.models.client_orm import ClientORM
from database.models.contact_orm import ContactORM

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


async def check_if_client_safe_to_delete(client_name: str) -> bool:
    return await Database.check_if_safe_to_delete(
        client_name,
        AddressORM.client_name,
        ApplicationORM.client_name,
        ContactORM.client_name,
    )


async def delete_client(client_name: str) -> str:
    return await Database.delete(ClientORM, ClientORM.name, client_name)
