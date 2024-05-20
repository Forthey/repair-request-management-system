from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
StrPrimKey = Annotated[str, mapped_column(primary_key=True)]


class CompanyPositionORM(Base):
    __tablename__ = "company_positions"

    name: Mapped[StrPrimKey]

    # Relationships


class ApplicationReasonORM(Base):
    __tablename__ = "application_reasons"

    reason_name: Mapped[str] = mapped_column(
        primary_key=True
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="cascade"),
        primary_key=True
    )


class CloseReasonORM(Base):
    __tablename__ = "close_reasons"

    name: Mapped[StrPrimKey]


class CompanyActivityORM(Base):
    __tablename__ = "activities"

    name: Mapped[StrPrimKey]
