from aiogram.fsm.state import StatesGroup, State


class ClientState(StatesGroup):
    # Add client
    writing_client_name = State()
    choosing_main_client = State()
    choosing_activity = State()
    add_client_confirmation = State()
