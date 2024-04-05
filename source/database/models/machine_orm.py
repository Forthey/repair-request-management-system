from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class MachineORM(Base):
    __tablename__ = "machines"

    id: Mapped[IntPrimKey]
    name: Mapped[str] = mapped_column(unique=True)
    photo_url: Mapped[str | None]
    release_year: Mapped[str]

    # Relationships

    applications: Mapped[list["ApplicationORM"]] = relationship(
        back_populates="machine"
    )
