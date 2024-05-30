from schemas.addresses import Address


def address_to_str(address: Address) -> str:
    return (
        f"    {address.name}\n"
        f"    Часы работы: {address.workhours if address.workhours else "Не указаны"}\n"
        f"    Заметки: {address.notes if address.notes else "Нету"}\n"
    )
