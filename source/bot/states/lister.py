from aiogram.fsm.state import StatesGroup, State


class ListerState(StatesGroup):
    listing = State()
