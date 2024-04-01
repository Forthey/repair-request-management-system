from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class AccessRightsORM(Base):
    __tablename__ = "access_rights"

    id: Mapped[IntPrimKey]
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]

    # TODO: relationships


class CompanyPositionsORM(Base):
    __tablename__ = "company_positions"

    id: Mapped[IntPrimKey]
    position: Mapped[str]

    # TODO: relationships


class ApplicationsReasonsORM(Base):
    __tablename__ = "applications_reasons"

    id: Mapped[IntPrimKey]
    reason: Mapped[str]


class RelReasonsApplicationsORM(Base):
    __tablename__ = "rel_reasons_applications"

    reason_id: Mapped[int] = mapped_column(
        ForeignKey("applications_reasons.id"),
        primary_key=True
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id"),
        primary_key=True
    )

    # TODO: relationships


class ActivitiesORM(Base):
    __tablename__ = "activities"

    id: Mapped[IntPrimKey]
    name: Mapped[str] = mapped_column(unique=True)
    notes: Mapped[str | None]

    # TODO: relationships
