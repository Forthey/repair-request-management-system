from sqlalchemy import select, and_, delete

from database.engine import async_session_factory
from database.models.address_orm import AddressORM
from database.models.application_orm import ApplicationORM
from database.queries.raw import Database
from schemas.addresses import AddressAdd, Address


async def get_address(client_name: str | None, address_name: str) -> Address | None:
    return await Database.get_one(AddressORM, Address, client_name=client_name, name=address_name)


async def add_address(address: AddressAdd) -> str | None:
    return await Database.add(
        AddressORM, AddressORM.name, **address.model_dump()
    )


async def find_address(client_name: str | None, address_name: str) -> bool:
    return await Database.find(AddressORM, client_name=client_name, name=address_name)


async def search_addresses(args: list[str]) -> list[Address]:
    return await Database.search(
        AddressORM, Address, {"name": AddressORM.name}, args, [AddressORM.name]
    )


async def address_belongs_to_client(client_name: str, address_name: str) -> bool:
    return (await get_address(client_name, address_name)) is not None


async def check_if_address_safe_to_delete(client_name: str | None, address_name: str) -> bool:
    async with async_session_factory() as session:
        query = (
            select(ApplicationORM.address_name)
            .where(
                and_(
                    ApplicationORM.address_name == address_name,
                    ApplicationORM.client_name == client_name
                )
            )
        )
        result = (await session.execute(query)).scalars().all()
        if result:
            return False
        return True


async def delete_address(client_name: str | None, address_name: str) -> str | None:
    async with async_session_factory() as session:
        query = (
            delete(AddressORM)
            .where(
                and_(
                    AddressORM.client_name == client_name,
                    AddressORM.name == address_name
                )
            )
            .returning(AddressORM.name)
        )

        try:
            address_name = (await session.execute(query)).scalar_one()

            await session.commit()
            return address_name
        except Exception as e:
            return None
