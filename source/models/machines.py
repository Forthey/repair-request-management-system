from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class MachinesORM(Base):
    __tablename__ = "machines"

    id: Mapped[IntPrimKey]
    name: Mapped[str] = mapped_column(unique=True)
    photo_url: Mapped[str | None]
    release_year: Mapped[str]

    # TODO: relationships
