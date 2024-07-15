from datetime import datetime
from pytz import timezone


def date_to_str(date: datetime) -> str:
    return date.astimezone(timezone("Europe/Moscow")).strftime("%d.%m.%Y %H:%M")
