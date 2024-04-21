from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
StrPrimKey = Annotated[str, mapped_column(primary_key=True)]


class MachineORM(Base):
    __tablename__ = "machines"

    name: Mapped[StrPrimKey]
    photo_url: Mapped[str | None]

    # Relationships
