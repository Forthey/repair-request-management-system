from schemas.workers import Worker


def worker_to_str(worker: Worker) -> str:
    return (
        f"id: {worker.telegram_id}\n"
        f"ФИО: {worker.name} {worker.surname} {worker.patronymic if worker.patronymic else ""}\n"
        f"Права доступа: {worker.access_right}\n"
        f"Активен: {"Да" if worker.active else "Нет"}"
    )
