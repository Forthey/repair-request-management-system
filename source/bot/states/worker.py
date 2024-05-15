from aiogram.fsm.state import StatesGroup, State


class WorkerState(StatesGroup):
    # Add worker
    writing_worker_username = State()
    writing_worker_fio = State()
    choosing_worker_access_rights = State()
    add_worker_confirmation = State()

    # Delete worker
    choosing_worker_to_delete = State()
    delete_worker_confirmation = State()

    # Update worker
    choosing_worker_to_update = State()
    choosing_worker_field = State()
    update_worker_confirmation = State()
