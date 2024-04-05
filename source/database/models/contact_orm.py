from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class ContactORM(Base):
    __tablename__ = "contacts"

    id: Mapped[IntPrimKey]
    name: Mapped[str]
    surname: Mapped[str]
    patronymic: Mapped[str | None]
    company_position_id: Mapped[int | None] = mapped_column(ForeignKey("company_positions.id", ondelete="SET NULL"))

    email: Mapped[str | None]
    phone1: Mapped[str | None]
    phone2: Mapped[str | None]
    phone3: Mapped[str | None]

    # Relationships

    company_position: Mapped["CompanyPositionORM"] = relationship(
        back_populates="contacts"
    )

    applications: Mapped[list["ApplicationORM"]] = relationship(
        back_populates="contact"
    )
