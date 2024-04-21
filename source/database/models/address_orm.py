from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
StrPrimKey = Annotated[str, mapped_column(primary_key=True)]


class AddressORM(Base):
    __tablename__ = 'addresses'

    name: Mapped[StrPrimKey]
    photo_url: Mapped[str | None]
    workhours: Mapped[str | None]

    client_name: Mapped[str] = mapped_column(ForeignKey("clients.name"))

    notes: Mapped[str | None]

    client: Mapped["ClientORM"] = relationship(
        cascade='all,delete',
        back_populates="addresses"
    )
