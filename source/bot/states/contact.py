from aiogram.fsm.state import StatesGroup, State


class ContactState(StatesGroup):
    writing_contact_fio = State()
    writing_contact_client_name = State()
    choosing_contact_company_position = State()
    writing_contact_email = State()
    writing_contact_phone_numbers = State()
    add_contact_confirmation = State()
    