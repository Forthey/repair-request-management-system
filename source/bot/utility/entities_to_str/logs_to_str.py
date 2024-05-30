from bot.utility.pretty_date import date_to_str
from schemas.applications import ApplicationChangeLog


def logs_to_str(logs: list[ApplicationChangeLog]) -> str:
    if len(logs) == 0:
        return "Нет изменений\n"

    result: str = ""
    for log in logs:
        result += f"({date_to_str(log.date)}) {log.field_name}: {log.old_value} -> {log.new_value}\n"

    print(result)
    return result
