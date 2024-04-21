from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated, Optional

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
StrPrimKey = Annotated[str, mapped_column(primary_key=True)]


class ClientORM(Base):
    __tablename__ = "clients"

    name: Mapped[StrPrimKey]
    main_client_name: Mapped[str | None] = mapped_column(ForeignKey("clients.name"))
    activity: Mapped[str] = mapped_column(ForeignKey("activities.name"))

    notes: Mapped[str | None]

    # Relationships
    addresses: Mapped[list["AddressORM"]] = relationship(
        back_populates="client"
    )

    contacts: Mapped[list["ContactORM"]] = relationship(
        back_populates="client"
    )

    applications: Mapped[list["ApplicationORM"]] = relationship(
        back_populates="client"
    )
