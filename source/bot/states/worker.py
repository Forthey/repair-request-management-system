from aiogram.fsm.state import StatesGroup, State


class AddWorkerState(StatesGroup):
    # Add worker
    writing_worker_username = State()
    writing_worker_fio = State()
    choosing_worker_access_rights = State()
    add_worker_confirmation = State()

    # Delete worker
    choosing_worker_to_delete = State()
    delete_worker_confirmation = State()


class OneWorkerState(StatesGroup):
    choosing_worker_id = State()
    choosing_worker_confirmation = State()
    listing_worker_apps = State()
