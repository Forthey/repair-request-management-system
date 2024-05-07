from sqlalchemy import ForeignKey, text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class WorkerORM(Base):
    __tablename__ = "workers"
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    name: Mapped[str]
    surname: Mapped[str]
    patronymic: Mapped[str | None]

    access_right: Mapped[str]

    # Relationships

    created_applications: Mapped[list["ApplicationORM"]] = relationship(
        primaryjoin="WorkerORM.telegram_id == ApplicationORM.editor_id",
        back_populates="editor"
    )

    taken_applications: Mapped[list["ApplicationORM"]] = relationship(
        primaryjoin="WorkerORM.telegram_id == ApplicationORM.repairer_id",
        back_populates="repairer"
    )
