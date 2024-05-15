from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.contact_orm import ContactORM
from schemas.contacts import ContactAdd, Contact


async def get_contact(contact_id: int) -> Contact | None:
    session = AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ContactORM)
            .where(ContactORM.id == contact_id)
        )

        contact_orm = (await session.execute(query)).scalar_one_or_none()

        return Contact.model_validate(contact_orm) if contact_orm else None


async def add_contact(contact: ContactAdd) -> int | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(ContactORM)
            .values(**contact.model_dump())
            .returning(ContactORM.id)
        )

        try:
            contact_id = (await session.execute(query)).scalar_one_or_none()

            await session.commit()
            return contact_id
        except IntegrityError:
            return None


async def search_contacts(client: str,
                          surname: str | None,
                          company_position: str | None) -> list[Contact]:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ContactORM)
            .where(
                ContactORM.client_name.icontains(client),
            )
        )

        if surname is not None:
            query = query.where(ContactORM.surname.icontains(surname))
        if company_position is not None:
            query = query.where(ContactORM.company_position.icontains(company_position))

        contacts_orm = (await session.execute(query)).scalars().all()

        return [Contact.model_validate(contact, from_attributes=True) for contact in contacts_orm]


async def contact_exists(contact_id: int) -> bool:
    session = AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ContactORM)
            .where(ContactORM.id == contact_id)
        )

        contact_orm = (await session.execute(query)).scalar_one_or_none()

        return contact_orm is not None
