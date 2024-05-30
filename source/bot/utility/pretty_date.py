from datetime import datetime


def date_to_str(date: datetime) -> str:
    return date.strftime("%d.%m.%Y %H:%M")
