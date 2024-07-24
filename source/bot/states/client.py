from aiogram.fsm.state import StatesGroup, State


class AddClientState(StatesGroup):
    writing_client_name = State()
    choosing_main_client = State()
    choosing_activity = State()
    add_client_confirmation = State()


class MergeClientsState(StatesGroup):
    choosing_main_client = State()
    choosing_other_client = State()
    merge_client_confirmation = State()
