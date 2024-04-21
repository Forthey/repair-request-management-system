from pydantic import BaseModel


class AccessRight(BaseModel):
    id: int
    name: str
    description: str


class CompanyPosition(BaseModel):
    name: str


class ApplicationReason(BaseModel):
    name: str


class CloseReason(BaseModel):
    name: str


class CompanyActivity(BaseModel):
    name: str
