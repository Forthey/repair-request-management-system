from pydantic import BaseModel


class ClientAdd(BaseModel):
    name: str
    main_client_name: str | None = None
    activity: str

    notes: str | None = None


class Client(ClientAdd):
    pass
