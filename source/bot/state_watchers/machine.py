from aiogram.fsm.state import StatesGroup, State


class MachineState(StatesGroup):
    # Add machine
    writing_machine_name = State()
    uploading_machine_photo = State()
