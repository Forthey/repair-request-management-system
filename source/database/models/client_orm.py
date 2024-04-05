from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated, Optional

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class ClientORM(Base):
    __tablename__ = "clients"

    id: Mapped[IntPrimKey]
    name: Mapped[str] = mapped_column(unique=True)
    main_client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"))
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"))

    notes: Mapped[str | None]

    # Relationships

    main_client: Mapped[Optional["ClientORM"]] = relationship()

    addresses: Mapped[list["AddressORM"]] = relationship(
        back_populates="client"
    )

    applications: Mapped[list["ApplicationORM"]] = relationship(
        back_populates="client"
    )

    activity: Mapped["ActivityORM"] = relationship(
        back_populates="clients"
    )
