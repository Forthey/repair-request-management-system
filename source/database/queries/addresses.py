from sqlalchemy import insert, select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from database.engine import async_session_factory
from database.models.address_orm import AddressORM
from database.queries.search import search_database
from schemas.addresses import AddressAdd, Address



async def get_address(client_name: str, address_name: str) -> Address | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(AddressORM)
            .where(
                and_(
                    AddressORM.client_name == client_name,
                    AddressORM.name == address_name
                )
            )
        )

        address_orm = (await session.execute(query)).scalar_one_or_none()

        return Address.model_validate(address_orm, from_attributes=True) if address_orm else None


async def add_address(address: AddressAdd) -> str | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(AddressORM)
            .values(**address.model_dump())
            .returning(AddressORM.name)
        )

        try:
            address_name = (await session.execute(query)).scalar_one_or_none()

            await session.commit()
            return address_name
        except IntegrityError:
            return None


async def address_exists(address: str) -> bool:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(count())
            .where(AddressORM.name == address)
        )

        return (await session.execute(query)).scalar_one() == 1


async def search_addresses(args: list[str]) -> list[Address]:
    return await search_database(
        AddressORM, {"name": AddressORM.name}, args, Address, [AddressORM.name]
    )


async def address_belongs_to_client(client_name: str, address: str) -> bool:
    address = get_address(client_name, address)
    return address is not None
