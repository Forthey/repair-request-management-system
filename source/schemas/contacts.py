from pydantic import BaseModel


class ContactAdd(BaseModel):
    name: str | None = None
    surname: str
    patronymic: str | None = None
    company_position: str | None = None
    client_name: str

    email: str | None = None
    phone1: str | None = None
    phone2: str | None = None
    phone3: str | None = None


class Contact(ContactAdd):
    id: int

