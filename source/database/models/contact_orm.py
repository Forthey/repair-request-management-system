from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
StrPrimKey = Annotated[str, mapped_column(primary_key=True)]


class ContactORM(Base):
    __tablename__ = "contacts"

    id: Mapped[IntPrimKey]

    name: Mapped[str | None]
    surname: Mapped[str | None]
    patronymic: Mapped[str | None]
    client_name: Mapped[str | None] = mapped_column(ForeignKey("clients.name"))
    company_position: Mapped[str | None] = mapped_column(ForeignKey("company_positions.name", ondelete="SET NULL"))

    email: Mapped[str | None]
    phone1: Mapped[str | None]
    phone2: Mapped[str | None]
    phone3: Mapped[str | None]

    # Relationships

    applications: Mapped[list["ApplicationORM"]] = relationship(
        back_populates="contact"
    )

    client: Mapped["ClientORM"] = relationship(
        back_populates="contacts"
    )
