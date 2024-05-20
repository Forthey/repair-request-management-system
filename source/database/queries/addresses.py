from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from database.engine import async_session_factory
from database.models.address_orm import AddressORM
from schemas.addresses import AddressAdd, Address


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
    session: AsyncSession
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(AddressORM)
                .order_by(AddressORM.name)
                .limit(50)
            )
            addresses_orm = (await session.execute(query)).scalars().all()

            return [Address.model_validate(address, from_attributes=True) for address in addresses_orm]

        query = (
            select(AddressORM)
            .where(AddressORM.name.icontains(args[0]))
            .order_by(AddressORM.name)
        )

        addresses_orm = (await session.execute(query)).scalars().all()

        addresses: list[Address] = []
        args = args[1:]
        for address in addresses_orm:
            arg_not_matched = False
            for arg in args:
                if arg.lower() not in str(address.name).lower():
                    arg_not_matched = True
                    break
            if not arg_not_matched:
                addresses.append(Address.model_validate(address, from_attributes=True))

        return addresses
