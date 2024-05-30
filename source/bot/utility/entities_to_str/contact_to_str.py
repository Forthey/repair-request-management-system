from schemas.contacts import Contact


def contact_to_str(contact: Contact) -> str:
    return (
        f"    id={contact.id}\n"
        f"    {contact.surname + " " if contact.surname is not None else ""}"
        f"{contact.name + " " if contact.name is not None else ""}"
        f"{contact.patronymic if contact.patronymic is not None else ""}\n"
        f"    {contact.email + "\n" if contact.email is not None else ""}"
        f"{contact.phone1 + "\n" if contact.phone1 is not None else ""}"
        f"{contact.phone2 + "\n" if contact.phone2 is not None else ""}"
        f"{contact.phone3 + "\n" if contact.phone3 is not None else ""}"
    )
