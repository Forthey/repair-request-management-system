from aiogram.fsm.state import StatesGroup, State


class CreateApplicationState(StatesGroup):
    choosing_main_application = State()

    choosing_client = State()

    choosing_app_reasons = State()

    choosing_machine = State()

    choosing_contact = State()

    choosing_address = State()

    writing_est_repair_date = State()

    writing_est_repair_duration_hours = State()

    choosing_notes = State()

    choosing_repairer = State()