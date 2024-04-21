from pydantic import BaseModel


class AddressAdd(BaseModel):
    name: str
    photo_url: str | None = None
    workhours: str | None = None

    client_name: str

    notes: str | None = None


class Address(AddressAdd):
    pass
