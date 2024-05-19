from sqlalchemy import insert, select, or_
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


async def search_contacts(args: list[str]) -> list[Contact]:
    session: AsyncSession
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(ContactORM)
                .order_by(ContactORM.name)
                .order_by(ContactORM.surname)
                .order_by(ContactORM.patronymic)
                .limit(50)
            )

            contacts = (await session.execute(query)).scalars().all()

            return [Contact.model_validate(contact, from_attributes=True) for contact in contacts]

        query = (
            select(ContactORM)
            .where(
                or_(
                    ContactORM.client_name.icontains(args[0]),
                    ContactORM.name.icontains(args[0]),
                    ContactORM.surname.icontains(args[0]),
                    ContactORM.patronymic.icontains(args[0]),
                    ContactORM.company_position.icontains(args[0])
                )
            )
            .order_by(ContactORM.name)
            .order_by(ContactORM.surname)
            .order_by(ContactORM.patronymic)
        )

        contacts_orm = (await session.execute(query)).scalars().all()
        print(contacts_orm)

        contacts: list[Contact] = []
        for contact in contacts_orm:
            for arg in args:
                if arg not in contact.client_name and \
                        arg not in str(contact.name) and \
                        arg not in str(contact.surname) and \
                        arg not in str(contact.patronymic) and \
                        arg not in str(contact.company_position):
                    break
                contacts.append(Contact.model_validate(contact, from_attributes=True))
                break

        return contacts


async def contact_exists(contact_id: int) -> bool:
    session = AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ContactORM)
            .where(ContactORM.id == contact_id)
        )

        contact_orm = (await session.execute(query)).scalar_one_or_none()

        return contact_orm is not None
