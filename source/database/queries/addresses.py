from database.models.address_orm import AddressORM
from database.queries.raw import Database
from schemas.addresses import AddressAdd, Address


async def get_address(client_name: str | None, address_name: str) -> Address | None:
    return await Database.get_one(AddressORM, Address, client_name=client_name, name=address_name)


async def add_address(address: AddressAdd) -> str | None:
    return await Database.add(
        AddressORM, AddressORM.name, **address.model_dump()
    )


async def find_address(client_name: str | None, address: str) -> bool:
    return await Database.find(AddressORM, client_name=client_name, name=address)


async def search_addresses(args: list[str]) -> list[Address]:
    return await Database.search(
        AddressORM, Address, {"name": AddressORM.name}, args, [AddressORM.name]
    )


async def address_belongs_to_client(client_name: str, address: str) -> bool:
    return (await get_address(client_name, address)) is not None
