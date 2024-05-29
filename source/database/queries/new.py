from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped

from database.database import Base
from database.engine import async_session_factory


async def add_to_database[ReturnType](
        table: type[Base],
        return_column: Mapped | None = None,
        **data
) -> ReturnType | None:
    async with async_session_factory() as session:
        query = (
            insert(table)
            .values(**data)
        )
        if return_column:
            query = query.returning(return_column)

        try:
            result = (await session.execute(query)).scalar_one_or_none()
        except IntegrityError:
            return None

        await session.commit()
        return result
