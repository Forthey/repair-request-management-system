from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.contact_orm import ContactORM
from schemas.contacts import ContactAdd, Contact


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
                ContactORM.surname.icontains(surname or ""),
                ContactORM.company_position.icontains(company_position or "")
            )
        )

        contacts_orm = (await session.execute(query)).scalars().all()

        return [Contact.model_validate(contact, from_attributes=True) for contact in contacts_orm]
