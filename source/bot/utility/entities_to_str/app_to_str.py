from schemas.applications import ApplicationFull, Application, ApplicationWithReasons


def full_app_to_str(app: ApplicationFull):
    result = (
        f"id = {app.id}\n"
        f"Заявка создана: {app.created_at.date()}\n"
        f"Причины заявки: {"; ".join(map(lambda reason: reason.name, app.reasons))}\n"
        f"Клиент: {app.client_name}\n"
    )

    if app.contact_id is None:
        result += "Контакт: не указан\n"
    else:
        result += (
            f"Контакт:\n"
            f"    id={app.contact_id}\n"
            f"    {app.contact.surname if app.contact.surname is not None else ""} "
            f"{app.contact.name if app.contact.name is not None else ""} "
            f"{app.contact.patronymic if app.contact.patronymic is not None else ""}\n"
            f"    {app.contact.email if app.contact.email is not None else ""} "
            f"{app.contact.phone1 if app.contact.phone1 is not None else ""} "
            f"{app.contact.phone2 if app.contact.phone2 is not None else ""} "
            f"{app.contact.phone3 if app.contact.phone3 is not None else ""}\n"
        )

    if app.machine_name is None:
        result += "Станок: Не указан\n"
    else:
        result += f"Станок: {app.machine_name}\n"

    if app.address_name is None:
        result += "Адрес: не указан\n"
    else:
        result += (
            f"Адрес: {app.address_name}\n"
            f"    Часы работы: {app.address.workhours if app.address.workhours is not None else "Не указаны"}\n"
            f"    Заметки: {app.address.notes if app.address.notes is not None else "Нету"}\n"
        )

    result += (
        f"Примерная дата ремонта: {
            app.est_repair_date.date() if app.est_repair_date is not None else "None"
        }\n"
        f"Примерное время ремонта: {app.est_repair_duration_hours if app.est_repair_duration_hours is not None else "0"}ч.\n"
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

    return result


def app_to_str(app: ApplicationFull | ApplicationWithReasons):
    return (
        f"id = {app.id}\n"
        f"Заявка создана: {app.created_at.date()}\n"
        f"id Клиента: {app.client_name}\n"
        f"Причины заявки: {"; ".join(map(lambda reason: reason.name, app.reasons))}\n"
        f"id Контакта: {app.contact_id}\n"
        f"Станок: {app.machine_name}\n"
        f"Адрес: {app.address_name}\n"
        f"Примерная дата ремонта: {
            app.est_repair_date.date() if app.est_repair_date is not None else "None"
        }\n"
        f"Примерное время ремонта: {app.est_repair_duration_hours if app.est_repair_duration_hours is not None else "0"}ч.\n"
        f"Статус: {"Закрыта" if app.closed_at is not None else "Свободна" if app.repairer_id is None else "Взята"}\n"
    )
