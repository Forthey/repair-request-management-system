from pydantic import BaseModel

from datetime import datetime


class ApplicationAdd(BaseModel):
    main_application_id: int | None

    est_repair_date: datetime
    est_repair_duration_hours: int | None

    editor_id: int
    repairer_id: int | None

    client: str
    contact_id: int | None

    address: str
    machine: str

    notes: str | None

    app_reasons: list["ApplicationReasonDTO"]


class Application(ApplicationAdd):
    id: int

    created_at: datetime
    updated_at: datetime

    closed_at: int | None
    close_reason: str | None


class ApplicationRel(Application):
    editor: "Worker"
    repairer: "Worker" | None
    contact: "Contact"