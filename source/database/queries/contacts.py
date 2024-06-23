from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory

from database.models.contact_orm import ContactORM

from database.queries.raw import Database

from schemas.contacts import ContactAdd, Contact


async def get_contact(contact_id: int) -> Contact | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ContactORM)
            .where(ContactORM.id == contact_id)
        )

        contact_orm = (await session.execute(query)).scalar_one_or_none()

        return Contact.model_validate(contact_orm, from_attributes=True) if contact_orm else None


async def add_contact(contact: ContactAdd) -> int | None:
    return await Database.add(
        ContactORM, ContactORM.id, **contact.model_dump()
    )


async def search_contacts(args: list[str]) -> list[Contact]:
    return await Database.search(
        ContactORM, Contact,
        {
            "client_name": ContactORM.client_name,
            "name": ContactORM.name,
            "surname": ContactORM.surname,
            "patronymic": ContactORM.patronymic,
            "company_position": ContactORM.company_position
        },
        args,
        [ContactORM.name, ContactORM.surname, ContactORM.patronymic]
    )


async def update_fields(contact_id: int, **fields) -> int | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            update(ContactORM)
            .where(ContactORM.id == contact_id)
            .values(**fields)
            .returning(ContactORM)
        )

        contact_id = (await session.execute(query)).scalar_one_or_none()

        await session.commit()
        return contact_id


async def find_contact(contact_id: int) -> bool:
    return await Database.find(ContactORM, id=contact_id)


async def contact_belongs_to_client(client_name: str, contact_id: int) -> bool:
    contact = await get_contact(contact_id)
    if contact is None:
        return False
    return contact.client_name == client_name or contact.client_name is None
