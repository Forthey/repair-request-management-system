from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.models.application_orm import ApplicationORM
from database.models.other_orms import RelReasonApplicationORM
from schemas.applications import ApplicationAdd


async def add_application(application: ApplicationAdd, app_reasons: list[str]) -> int | None:
    session: AsyncSession
    async with async_session_factory() as session:
        query = (
            insert(ApplicationORM)
            .values(**application.model_dump())
            .returning(ApplicationORM.id)
        )

        try:
            app_id = (await session.execute(query)).scalar_one_or_none()

            for reason in app_reasons:
                session.add(RelReasonApplicationORM(application_id=app_id, reason_name=reason))

            await session.commit()
            return app_id
        except IntegrityError:
            return None
