from typing import Optional

from pydantic import BaseModel

from datetime import datetime

from schemas.machines import Machine
from schemas.addresses import Address
from schemas.contacts import Contact
from schemas.other import ApplicationReason


class ApplicationAdd(BaseModel):
    est_repair_date: datetime | None = None
    est_repair_duration_hours: int | None = None

    editor_id: int
    repairer_id: int | None = None

    client_name: str | None = None
    contact_id: int

    address_name: str | None = None
    machine_name: str | None = None

    notes: str | None = None


class Application(ApplicationAdd):
    id: int

    created_at: datetime

    closed_at: datetime | None
    close_reason: str | None


class ApplicationWithReasons(Application):
    reasons: list["ApplicationReason"]


class ApplicationFull(ApplicationWithReasons):
    machine: Optional[Machine]
    address: Optional[Address]
    contact: Optional[Contact]


class ApplicationChangeLogAdd(BaseModel):
    application_id: int
    field_name: str
    old_value: str | None
    new_value: str | None


class ApplicationChangeLog(ApplicationChangeLogAdd):
    id: int
    date: datetime
