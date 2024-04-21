from pydantic import BaseModel


class Machine(BaseModel):
    name: str
    photo_url: str | None
