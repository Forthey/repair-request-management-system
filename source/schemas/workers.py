from pydantic import BaseModel


class WorkerAdd(BaseModel):
    telegram_id: int

    name: str
    surname: str
    patronymic: str | None

    access_right: str


class Worker(WorkerAdd):
    pass
