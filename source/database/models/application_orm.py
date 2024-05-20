from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated, Optional

from database.database import Base

from database.models.client_orm import ClientORM
from database.models.contact_orm import ContactORM
from database.models.machine_orm import MachineORM
from database.models.address_orm import AddressORM
from database.models.other_orms import ApplicationReasonORM


IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class ApplicationORM(Base):
    __tablename__ = "applications"

    id: Mapped[IntPrimKey]

    created_at: Mapped[CreateDate]

    est_repair_date: Mapped[datetime | None]
    est_repair_duration_hours: Mapped[int | None]

    editor_id: Mapped[int] = mapped_column(ForeignKey("workers.telegram_id"))
    repairer_id: Mapped[int | None] = mapped_column(ForeignKey("workers.telegram_id"))

    client_name: Mapped[int | None] = mapped_column(ForeignKey("clients.name", ondelete="SET NULL"))
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"))

    address_name: Mapped[str | None] = mapped_column(ForeignKey("addresses.name", ondelete="SET NULL"))
    machine_name: Mapped[str | None] = mapped_column(ForeignKey("machines.name", ondelete="SET NULL"))

    closed_at: Mapped[datetime | None]
    close_reason: Mapped[str | None] = mapped_column(ForeignKey("close_reasons.name", ondelete="SET NULL"))

    notes: Mapped[str | None]

    # Relationships
    reasons: Mapped[list[ApplicationReasonORM]] = relationship()

    editor: Mapped["WorkerORM"] = relationship(
        foreign_keys=[editor_id],
        back_populates="created_applications"
    )

    client: Mapped[ClientORM] = relationship(
        back_populates="applications"
    )

    address: Mapped[Optional[AddressORM]] = relationship()

    machine: Mapped[Optional[MachineORM]] = relationship()

    repairer: Mapped[Optional["WorkerORM"]] = relationship(
        foreign_keys=[repairer_id],
        back_populates="taken_applications"
    )

    contact: Mapped[Optional[ContactORM]] = relationship(
        foreign_keys=[contact_id],
        back_populates="applications"
    )


class ApplicationChangeLogORM(Base):
    __tablename__ = "applications_change_log"

    id: Mapped[IntPrimKey]
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"))
    field_name: Mapped[str]
    old_value: Mapped[str | None]
    new_value: Mapped[str | None]
    date: Mapped[CreateDate]
