from aiogram.fsm.state import StatesGroup, State


class AddressState(StatesGroup):
    # Add address
    writing_address = State()
    choosing_client = State()
    choosing_photo = State()
    writing_workhours = State()
    writing_notes = State()
    add_address_confirmation = State()
