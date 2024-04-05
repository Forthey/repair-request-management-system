from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class CompanyPositionORM(Base):
    __tablename__ = "company_positions"

    id: Mapped[IntPrimKey]
    position: Mapped[str]

    # Relationships

    contacts: Mapped[list["ContactORM"]] = relationship(
        back_populates="company_position"
    )


class ApplicationReasonORM(Base):
    __tablename__ = "applications_reasons"

    id: Mapped[IntPrimKey]
    reason: Mapped[str]

    # Relationships

    applications: Mapped[list["ApplicationORM"]] = relationship(
        back_populates="reasons",
        secondary="rel_reasons_applications"
    )


class RelReasonApplicationORM(Base):
    __tablename__ = "rel_reasons_applications"

    reason_id: Mapped[int] = mapped_column(
        ForeignKey("applications_reasons.id", ondelete="cascade"),
        primary_key=True
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="cascade"),
        primary_key=True
    )


class CloseReasonORM(Base):
    __tablename__ = "close_reasons"

    id: Mapped[IntPrimKey]
    reason: Mapped[str] = mapped_column(unique=True)

    # Relationships

    applications: Mapped[list["ApplicationORM"]] = relationship(
        back_populates="close_reason"
    )


class ActivityORM(Base):
    __tablename__ = "activities"

    id: Mapped[IntPrimKey]
    name: Mapped[str] = mapped_column(unique=True)

    # Relationships

    clients: Mapped[list["ClientORM"]] = relationship(
        back_populates="activity"
    )
