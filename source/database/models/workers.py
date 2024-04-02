from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class WorkersORM(Base):
    __tablename__ = "workers"

    id: Mapped[IntPrimKey]
    telegram_id: Mapped[int] = mapped_column(unique=True)

    name: Mapped[str]
    surname: Mapped[str]
    patronymic: Mapped[str | None]

    access_rights_id: Mapped[int] = mapped_column(ForeignKey("access_rights.id"))
