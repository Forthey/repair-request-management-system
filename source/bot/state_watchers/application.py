from aiogram.fsm.state import StatesGroup, State
from bot.state_watchers.machine import MachineState


class ApplicationState(StatesGroup):
    # Create application
    choosing_main_application = State()
    choosing_app_client = State()
    choosing_app_reasons = State()
    choosing_app_machine = State()
    choosing_app_contact = State()
    choosing_app_address = State()
    writing_app_est_repair_date = State()
    writing_app_est_repair_duration_hours = State()
    writing_app_notes = State()
    choosing_app_repairer = State()
