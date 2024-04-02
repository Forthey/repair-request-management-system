from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from typing import Annotated

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class ApplicationsORM(Base):
    __tablename__ = "applications"

    id: Mapped[IntPrimKey]
    main_application_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id"))

    created_at: Mapped[CreateDate]
    updated_at: Mapped[CreateDate]

    est_repair_date: Mapped[datetime | None]
    est_repair_duration_hours: Mapped[int | None]

    editor_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    repairer_id: Mapped[int | None] = mapped_column(ForeignKey("workers.id"))

    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"))
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))

    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"))

    closed_at: Mapped[datetime | None]
    close_reason: Mapped[datetime | None]

    notes: Mapped[str | None]

    # TODO: relationships
