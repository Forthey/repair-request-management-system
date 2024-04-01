from typing import Annotated

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String


MetaStr = Annotated[str, 200]
InfoStr = Annotated[str, 1000]


class Base(DeclarativeBase):
    type_annotation_map = {
        MetaStr: String(200),
        InfoStr: String(1000)
    }

    def __repr__(self):
        columns = []
        for column in self.__table__.columns.keys():
            columns.append(f"{column}={getattr(self, column)}")

        return f"({self.__class__.__name__})\n\t {",\n\t".join(columns)}"
