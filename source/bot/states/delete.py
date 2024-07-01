from aiogram.fsm.state import StatesGroup, State


class DeleteState(StatesGroup):
    choosing_entity = State()

    # Client
    choosing_client_name_to_delete = State()
    delete_client_confirmation = State()

    # Address
    choosing_client_name_to_address = State()
    choosing_address_name_to_delete = State()
    delete_address_confirmation = State()

    # Contact
    choosing_contact_id_to_delete = State()
    delete_contact_confirmation = State()

    # Machine
    choosing_machine_name_to_delete = State()
    delete_machine_confirmation = State()



