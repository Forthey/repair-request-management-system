from typing import Optional

from pydantic import BaseModel

from datetime import datetime


class ApplicationAdd(BaseModel):
    main_application_id: int | None = None

    est_repair_date: datetime | None = None
    est_repair_duration_hours: int | None = None

    editor_id: int
    repairer_id: int | None = None

    client_name: str
    contact_id: int | None = None

    address: str
    machine: str

    notes: str | None = None


class Application(ApplicationAdd):
    id: int

    created_at: datetime
    updated_at: datetime

    closed_at: int | None
    close_reason: str | None


class ApplicationRel(Application):
    editor: "Worker"
    repairer: Optional["Worker"]
    contact: "Contact"