
app_strings = [
    "заявка"
]

worker_strings = [
    "работник"
]

machine_strings = [
    "машина",
    "станок",
    "чпу"
]

app_reason_strings = [
    "причина_заявки",
    "п-з"
]

close_reason_strings = [
    "причина_закрытия_заявки",
    "п-з-з"
]

company_activity_strings = [
    "деятельность_компании",
    "д-к"
]

company_position_strings = [
    "позиция",
    "должность",
]

client_strings = [
    "клиент",
    "компания"
]

contact_strings = [
    "контакт"
]

address_strings = [
    "адрес"
]


def concat_strings() -> list[str]:
    return (
            app_strings +
            worker_strings +
            machine_strings +
            app_reason_strings +
            close_reason_strings +
            company_activity_strings +
            company_position_strings +
            client_strings +
            contact_strings +
            address_strings
    )


all_strings = concat_strings()
