from aiogram.fsm.state import StatesGroup, State


class NewState(StatesGroup):
    # Add machine
    choosing_entity = State()
