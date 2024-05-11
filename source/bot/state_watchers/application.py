from aiogram.fsm.state import StatesGroup, State
from bot.state_watchers.machine import MachineState


class ApplicationState(StatesGroup):
    # Add application
    choosing_app_main_application = State()
    choosing_app_client = State()
    choosing_app_contact = State()
    choosing_app_reasons = State()
    choosing_app_machine = State()
    choosing_app_address = State()
    writing_app_est_repair_date_and_duration = State()
    writing_app_notes = State()
    choosing_app_repairer = State()
    add_app_confirmation = State()


class TakeApplicationState(StatesGroup):
    choosing_app_id = State()
    take_app_confirmation = State()


class EditApplicationState(StatesGroup):
    choosing_app_id = State()
    waiting_for_click = State()
    choosing_app_contact = State()
    choosing_app_reasons = State()
    choosing_app_machine = State()
    choosing_app_address = State()
    editing_app_est_repair_date_and_duration = State()
    editing_app_notes = State()
    edit_app_confirmation = State()
