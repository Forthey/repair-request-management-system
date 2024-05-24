from sqlalchemy import insert, select, or_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory

from database.models.contact_orm import ContactORM

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
                .order_by(ContactORM.name, ContactORM.surname, ContactORM.patronymic)
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
        args = args[1:]
        for contact in contacts_orm:
            arg_not_matched = False
            for arg in args:
                if arg.lower() not in str(contact.client_name).lower() and \
                        arg.lower() not in str(contact.name).lower() and \
                        arg.lower() not in str(contact.surname).lower() and \
                        arg.lower() not in str(contact.patronymic).lower() and \
                        arg.lower() not in str(contact.company_position).lower():
                    arg_not_matched = True
                    break
            if not arg_not_matched:
                contacts.append(Contact.model_validate(contact, from_attributes=True))

        return contacts


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


async def contact_exists(contact_id: int) -> bool:
    session = AsyncSession
    async with async_session_factory() as session:
        query = (
            select(ContactORM)
            .where(ContactORM.id == contact_id)
        )

        contact_orm = (await session.execute(query)).scalar_one_or_none()

        return contact_orm is not None


async def contact_belongs_to_client(client_name: str, contact_id: int) -> bool:
    contact = await get_contact(contact_id)
    if contact is None:
        return False
    return contact.client_name == client_name or contact.client_name is None
