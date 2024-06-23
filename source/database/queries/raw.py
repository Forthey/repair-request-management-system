from pydantic import BaseModel
from sqlalchemy import select, UnaryExpression, insert, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, QueryableAttribute, selectinload

from database.database import Base
from database.engine import async_session_factory


class Database:
    @staticmethod
    async def get_one[Table, Schema](
            table: type(Table), schema: type(Schema),
            join: list[QueryableAttribute] | None = None,
            **filters
    ) -> Schema | None:
        async with async_session_factory() as session:
            query = (
                select(table)
                .filter_by(**filters)
            )
            if join:
                query = query.options(*map(lambda join_el: selectinload(join_el), join))

            result_orm = (await session.execute(query)).scalar_one_or_none()

            return schema.model_validate(result_orm, from_attributes=True) if result_orm else None

    @staticmethod
    async def get[Table, Schema](
            table: type(Table), schema: type(Schema),
            ordering: list[UnaryExpression] | None = None,
            offset: int | None = None, limit: int | None = None,
            join: list[QueryableAttribute] | None = None,
            **filters,
    ) -> list[Schema]:
        async with async_session_factory() as session:
            query = (
                select(table)
                .filter_by(**filters)
            )
            if join:
                query = query.options(*map(lambda join_el: selectinload(join_el), join))
            if ordering:
                query = query.order_by(*ordering)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result_orm = (await session.execute(query)).scalar_one_or_none()

            return [schema.model_validate(res, from_attributes=True) for res in result_orm]

    @staticmethod
    async def add[Table, ReturnType](table: type[Table], return_column: Mapped | None = None,
                                     **data) -> ReturnType | None:
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

    @staticmethod
    async def search[Table, Schema](
            table: type[Table], schema: type[Schema],
            columns: dict[str, Mapped], args: list[str],
            ordering: list[UnaryExpression], **filters) -> list[Schema]:
        async with async_session_factory() as session:
            if len(args) == 0:
                query = (
                    select(table)
                    .filter_by(**filters)
                    .order_by(*ordering)
                    .limit(50)
                )

                results_orm = (await session.execute(query)).scalars().all()
                return [schema.model_validate(result, from_attributes=True) for result in results_orm]

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

            results_orm = (await session.execute(query)).scalars().all()

            filtered_results: list[schema] = list()
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
                    filtered_results.append(schema.model_validate(result, from_attributes=True))

            return filtered_results

    @staticmethod
    async def find[Table](table: type(Table), **filters) -> bool:
        async with async_session_factory() as session:
            query = (
                select(
                    select(table)
                    .filter_by(**filters)
                    .exists()
                )
            )

            return (await session.execute(query)).scalar_one()
