from schemas.clients import Client


def client_to_str(client: Client) -> str:
    return (f"Имя: {client.name}\n"
            f"Родительская компания: {client.main_client_name if client.main_client_name else "Отсутствует"}\n"
            f"Деятельность: {client.activity if client.activity else "Не указана"}\n"
            f"Заметки: {client.notes if client.notes else "Нету"}")
