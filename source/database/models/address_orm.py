from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class AddressORM(Base):
    __tablename__ = 'addresses'

    id: Mapped[IntPrimKey]
    address: Mapped[str] = mapped_column(unique=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    photo_url: Mapped[str | None]
    workhours: Mapped[str | None]
    notes: Mapped[str | None]

    client: Mapped["ClientORM"] = relationship(
        cascade='all,delete',
        back_populates="addresses"
    )

    applications: Mapped[list["ApplicationORM"]] = relationship(
        back_populates="address",
    )
