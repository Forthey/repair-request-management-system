import datetime
import logging
import re

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import database.queries.applications as db_apps
import database.queries.clients as db_clients
import database.queries.contacts as db_contacts
import database.queries.machines as db_machines
import database.queries.addresses as db_addresses
from bot.utility.render_buttons import render_inline_buttons
from schemas.addresses import Address, AddressAdd
from schemas.contacts import ContactAdd


async def parse_app_client(message: Message, state: FSMContext) -> bool:
    client_name = message.text
    if not await db_clients.find_client(client_name):
        await message.answer(
            f"Клиента \"{client_name}\" не существует. Создать его?",
            reply_markup=render_inline_buttons({"yes_to_add_client": "Да", "no_to_add_client": "Нет"}, 2)
        )
        await state.update_data(tmp_client_name=client_name)
        return False

    contact_id = (await state.get_data()).get("contact_id")

    if contact_id is not None:
        if not await db_contacts.contact_belongs_to_client(client_name, contact_id):
            await message.answer(f"Контакт {contact_id}, указанный ранее, не относится к клиенту \"{client_name}\"")
            return False
        await db_contacts.update_fields(contact_id, client_name=client_name)

    address = (await state.get_data()).get("address_name")
    if address is not None and not db_addresses.address_belongs_to_client(client_name, address):
        await message.answer(f"Адрес {address}, указанный ранее, не относится к клиенту \"{client_name}\"")
        return False

    await state.update_data(client=(await db_clients.get_client(client_name)))
    await state.update_data(client_name=client_name)
    return True


async def parse_app_contact(message: Message, state: FSMContext) -> bool:
    contact_id = ""
    client_name = (await state.get_data()).get("client_name")
    args = message.text.split(" ")
    if args[0] == "/add":
        contact: ContactAdd
        if len(args) != 3:
            await message.answer("Неправильный формат команды /add")
            return False
        name = args[1]
        if re.match(r"[^@]+@[^@]+\.[^@]+", args[2]):
            contact = ContactAdd(name=name, email=args[2], client_name=client_name)
        else:
            contact = ContactAdd(name=name, phone1=args[2], client_name=client_name)

        contact_id = await db_contacts.add_contact(contact)
    else:
        contact_id = message.text
        try:
            contact_id = int(contact_id)
        except ValueError:
            await message.answer("Указан не id")
            return False
        if not await db_contacts.find_contact(int(contact_id)):
            await message.answer("Контакта с таким id не существует")
            return False
        if client_name is not None and not await db_contacts.contact_belongs_to_client(client_name, contact_id):
            await message.answer(f"Контакт {contact_id} не относится к клиенту \"{client_name}\", добавленному ранее")
            return False

    await state.update_data(contact=(await db_contacts.get_contact(contact_id)))
    await state.update_data(contact_id=contact_id)
    return True


async def parse_app_reason(message: Message, state: FSMContext) -> bool:
    reason = message.text
    reasons = (await state.get_data()).get("app_reasons")
    if reasons is None:
        reasons: list[str] = [reason]
    else:
        for added_reason in reasons:
            if added_reason == reason:
                await message.answer("Такая причина уже была добавлена")
                return False
        reasons.append(reason)

    await state.update_data(app_reasons=reasons)
    return True


async def parse_app_machine(message: Message, state: FSMContext) -> bool:
    machine_name = message.text
    if not await db_machines.find_machine(machine_name):
        await message.answer(
            f"Станка \"{machine_name}\" не существует. Создать его?",
            reply_markup=render_inline_buttons({"yes_to_add_machine": "Да", "no_to_add_machine": "Нет"}, 2)
        )
        await state.update_data(tmp_machine_name=machine_name)
        return False

    await state.update_data(machine=(await db_machines.get_machine(machine_name)))
    await state.update_data(machine_name=machine_name)
    return True


async def parse_app_address(message: Message, state: FSMContext) -> bool:
    args = message.text.split(" ")
    client_name = (await state.get_data()).get("client_name")
    address_name: str

    if not client_name:
        await message.answer("Клиент не выбран, невозможно указать адрес")
        return False

    if args[0] == "/add":
        if len(args) == 1:
            await message.answer("Неправильный формат команды /add")
            return False

        address_name = " ".join(args[1:])
        if not await db_addresses.add_address(AddressAdd(client_name=client_name, name=address_name)):
            await message.answer("Такое адрес уже существует")
            return False
    else:
        address_name = message.text
        address: Address | None = await db_addresses.get_address(client_name, address_name)
        if address is None:
            await message.answer(
                f"Адреса \"{address_name}\" у клиента \"{client_name}\" не существует. Создать его?",
                reply_markup=render_inline_buttons({"yes_to_add_address": "Да", "no_to_add_address": "Нет"}, 2)
            )
            await state.update_data(tmp_address_name=address_name)
            return False

    await state.update_data(address=(await db_addresses.get_address(client_name, address_name)))
    await state.update_data(address_name=address_name)
    return True


async def parse_app_est_repair_date_and_duration(message: Message, state: FSMContext) -> bool:
    args = message.text.split(" ")
    if not (1 <= len(args) <= 2):
        await message.answer("Неправильный формат")
        return False
    if len(args) > 0:
        if not re.match(r"^[0-3][0-9].[0-1][0-9].20[2-9][0-9]$", args[0]):
            await message.answer("Неправильный формат даты")
            return False

        date_args = args[0].split(".")
        est_repair_date = datetime.datetime(int(date_args[2]), int(date_args[1]), int(date_args[0]))
        await state.update_data(est_repair_date=est_repair_date)
    if len(args) > 1:
        try:
            est_repair_duration_hours = int(args[1])
        except ValueError:
            await message.answer("Длительность ремонта указана неверно")
            return False
        await state.update_data(est_repair_duration_hours=est_repair_duration_hours)

    return True
