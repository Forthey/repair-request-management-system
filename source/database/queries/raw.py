from pydantic import BaseModel
from sqlalchemy import select, UnaryExpression, insert, or_, delete
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

    @staticmethod
    async def check_if_safe_to_delete(key_value, *references: Mapped) -> bool:
        async with async_session_factory() as session:
            for reference in references:
                query = (
                    select(reference)
                    .where(reference == key_value)
                )
                result = (await session.execute(query)).scalars().all()
                if result:
                    return False

            return True

    @staticmethod
    async def delete[Table, KeyRowType](table: type(Table), key_row: Mapped, key_value: KeyRowType) -> KeyRowType | None:
        async with async_session_factory() as session:
            query = (
                delete(table)
                .where(key_row == key_value)
                .returning(key_row)
            )

            try:
                key_value = (await session.execute(query)).scalar_one()

                await session.commit()
                return key_value
            except Exception as e:
                return None
