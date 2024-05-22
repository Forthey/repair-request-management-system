from bot.utility.entities_to_str.contact_to_str import contact_to_str
from database.queries.contacts import get_contact
from schemas.applications import ApplicationFull, Application, ApplicationWithReasons


def full_app_to_str(app: ApplicationFull):
    result = (
        f"id = {app.id}\n"
        f"Заявка создана: {app.created_at.date()}\n"
        f"Причины заявки: {"; ".join(map(lambda reason: reason.reason_name, app.reasons))}\n"
        f"Клиент: {app.client_name if app.client_name else "Не указан"}\n"
    )

    if app.contact_id is None:
        result += "Контакт: не указан\n"
    else:
        result += f"Контакт:\n {contact_to_str(app.contact)}"

    if app.machine_name is None:
        result += "Станок: Не указан\n"
    else:
        result += f"Станок: {app.machine_name}\n"

    if app.address_name is None:
        result += "Адрес: не указан\n"
    else:
        result += (
            f"Адрес: {app.address_name}\n"
            f"    Часы работы: {app.address.workhours if app.address.workhours else "Не указаны"}\n"
            f"    Заметки: {app.address.notes if app.address.notes else "Нету"}\n"
        )

    result += (
        f"Примерная дата ремонта: {
            app.est_repair_date.date() if app.est_repair_date else "Не указана"
        }\n"
        f"Примерное время ремонта: {app.est_repair_duration_hours if app.est_repair_duration_hours else "0"}ч.\n"
    )

    if app.closed_at is not None:
        result += (
            f"Статус: Закрыта\n"
            f"Причина закрытия: {app.close_reason}\n"
        )
    elif app.repairer_id is not None:
        result += "Статус: Взята\n"
    else:
        result += "Статус: Свободна\n"

    result += f"Заметки: {app.notes if app.notes else "Нету"}\n"
    return result


def app_to_str(app: ApplicationFull | ApplicationWithReasons):
    return (
        f"id = {app.id}\n"
        f"Заявка создана: {app.created_at.date()}\n"
        f"Клиент: {app.client_name if app.client_name else "Не указан"}\n"
        f"Причины заявки: {"; ".join(map(lambda reason: reason.reason_name, app.reasons))}\n"
        f"Контакт:\n {app.contact_id if app.contact_id is not None else "Не указан"}"
        f"Станок: {app.machine_name}\n"
        f"Адрес: {app.address_name}\n"
        f"Примерная дата ремонта: {
            app.est_repair_date.date() if app.est_repair_date is not None else "None"
        }\n"
        f"Примерное время ремонта: {app.est_repair_duration_hours if app.est_repair_duration_hours is not None else "0"}ч.\n"
        f"Статус: {"Закрыта" if app.closed_at is not None else "Свободна" if app.repairer_id is None else "Взята"}\n"
    )
