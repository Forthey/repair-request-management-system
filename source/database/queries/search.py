import logging
from sqlalchemy import or_

from sqlalchemy import select
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.elements import UnaryExpression

from database.database import Base
from database.engine import async_session_factory


async def search_database[Schema](
        table: type[Base],
        columns: dict[str, Mapped],
        args: list[str],
        pydantic_schema: type[Schema],
        ordering: list[UnaryExpression],
        **filters
) -> list[Schema]:
    async with async_session_factory() as session:
        if len(args) == 0:
            query = (
                select(table)
                .filter_by(**filters)
                .order_by(*ordering)
                .limit(50)
            )

            results_orm = (await session.execute(query)).scalars().all()
            return [pydantic_schema.model_validate(result, from_attributes=True) for result in results_orm]

        query = (
            select(table)
            .order_by(*ordering)
            .filter_by(**filters)
            .where(
                or_(
                    *map(lambda col: columns[col].icontains(args[0]), columns)
                )
            )
        )

        logging.info(query)

        results_orm = (await session.execute(query)).scalars().all()

        filtered_results: list[Schema] = list()
        args = args[1:]
        for result in results_orm:
            arg_not_matched = False
            for arg in args:
                column_match_found = False
                for column_name in columns:
                    if arg.lower() in str(getattr(result, str(column_name))).lower():
                        column_match_found = True
                        break
                if not column_match_found:
                    arg_not_matched = True
            if not arg_not_matched:
                filtered_results.append(pydantic_schema.model_validate(result, from_attributes=True))

        return filtered_results
