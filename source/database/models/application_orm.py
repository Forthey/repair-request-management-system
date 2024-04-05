from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from typing import Annotated, Optional

from database.database import Base

IntPrimKey = Annotated[int, mapped_column(primary_key=True)]
CreateDate = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class ApplicationORM(Base):
    __tablename__ = "applications"

    id: Mapped[IntPrimKey]
    main_application_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id"))

    created_at: Mapped[CreateDate]
    updated_at: Mapped[CreateDate]

    est_repair_date: Mapped[datetime | None]
    est_repair_duration_hours: Mapped[int | None]

    editor_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id", ondelete="SET NULL"))
    repairer_id: Mapped[int | None] = mapped_column(ForeignKey("workers.id"))

    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"))
    address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id", ondelete="SET NULL"))
    machine_id: Mapped[int | None] = mapped_column(ForeignKey("machines.id", ondelete="SET NULL"))

    closed_at: Mapped[datetime | None]
    close_reason_id: Mapped[int | None] = mapped_column(ForeignKey("close_reasons.id", ondelete="SET NULL"))

    notes: Mapped[str | None]

    # Relationships
    reasons: Mapped[list["ApplicationReasonORM"]] = relationship(
        back_populates="applications",
        secondary="rel_reasons_applications",
    )

    editor: Mapped["WorkerORM"] = relationship(
        foreign_keys=[editor_id],
        back_populates="created_applications"
    )

    client: Mapped["ClientORM"] = relationship(
        back_populates="applications"
    )

    repairer: Mapped[Optional["WorkerORM"]] = relationship(
        foreign_keys=[repairer_id],
        back_populates="taken_applications"
    )

    contact: Mapped["ContactORM"] = relationship(
        back_populates="applications"
    )

    address: Mapped["AddressORM"] = relationship(
        back_populates="applications"
    )

    machine: Mapped["MachineORM"] = relationship(
        back_populates="applications"
    )

    close_reason: Mapped[Optional["CloseReasonORM"]] = relationship(
        back_populates="applications"
    )
