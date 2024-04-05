from aiogram.fsm.state import StatesGroup, State


class AddWorkerState(StatesGroup):
    writing_username = State()

    writing_name = State()

    writing_surname = State()

    writing_patronymic = State()

    choosing_access_rights = State()

    confirmation = State()


class AddWorkerFSM:
    fsm_array = [
        AddWorkerState.writing_username,
        AddWorkerState.writing_name,
        AddWorkerState.writing_surname,
        AddWorkerState.writing_patronymic,
        AddWorkerState.choosing_access_rights,
        AddWorkerState.confirmation
    ]

    @staticmethod
    def begin():
        return AddWorkerFSM.fsm_array[0]

    @staticmethod
    def next(state: State | str) -> State:
        index = AddWorkerFSM.fsm_array.index(state)
        if index == len(AddWorkerFSM.fsm_array) - 1:
            return state
        return AddWorkerFSM.fsm_array[index + 1]

    @staticmethod
    def prev(state: State | str) -> State:
        index = AddWorkerFSM.fsm_array.index(state)
        if index == 0:
            return state
        return AddWorkerFSM.fsm_array[index - 1]
