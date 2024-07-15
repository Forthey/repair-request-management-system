from aiogram.fsm.state import StatesGroup, State


class AddApplicationState(StatesGroup):
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


class ChooseOneApplicationState(StatesGroup):
    choosing_app_id = State()
    chosen_app_confirmation = State()
    writing_app_close_reason = State()

    choosing_repairer_id = State()
    app_transfer_confirmation = State()


class EditApplicationState(StatesGroup):
    choosing_app_id = State()
    waiting_for_choose_confirmation = State()
    waiting_for_click = State()
    choosing_app_contact = State()
    choosing_app_reasons = State()
    choosing_app_machine = State()
    choosing_app_address = State()
    editing_app_est_repair_date_and_duration = State()
    editing_app_notes = State()
    edit_app_confirmation = State()


class ApplicationListsState(StatesGroup):
    list_by_worker = State()


add_states_strings: dict[State, str] = {
    AddApplicationState.choosing_app_client:
        "Введите имя клиента (компании), подавшего заявку",
    AddApplicationState.choosing_app_contact:
        "Введите id контакта, привязанного к клиенту "
        "(или привяжите новый контакт к клиенту, используя команду /add:\n"
        "/add Имя +790012088\n"
        "/add Имя example@gmail.com)\n",
    AddApplicationState.choosing_app_reasons:
        "Введите причины подачи заявки (когда закончите - нажмите 'Далее')",
    AddApplicationState.choosing_app_machine:
        "Введите название станка",
    AddApplicationState.choosing_app_address:
        "Введите адрес, на который необходимо будет выехать "
        "(или привяжите новые адрес к компании, используя команду /add: "
        "/add Пример Адреса)",
    AddApplicationState.writing_app_est_repair_date_and_duration:
        "Введите примерную дату ремонта (формат XX.XX.XXXX) "
        "и через пробел примерное время, необходимое на ремонт (в часах) "
        "(Необязатльное поле)",
    AddApplicationState.writing_app_notes:
        "Напишите допольнительную информацию, которую не удалось поместить в поля выше"
        "(Необязательное поле)",
}

edit_states_strings: dict[State, str] = {
    EditApplicationState.choosing_app_contact:
        "Введите id контакта, привязанного к клиенту "
        "(или привяжите новый контакт к клиенту, используя команду /add:\n"
        "/add Имя +790012088\n"
        "/add Имя example@gmail.com)\n",
    EditApplicationState.choosing_app_reasons:
        "Введите причину подачи заявки",
    EditApplicationState.choosing_app_machine:
        "Введите название станка",
    EditApplicationState.choosing_app_address:
        "Введите адрес, на который необходимо будет выехать "
        "(или привяжите новые адрес к компании, используя команду /add: "
        "/add Пример Адреса)",
    EditApplicationState.editing_app_est_repair_date_and_duration:
        "Введите примерную дату ремонта (формат XX.XX.XXXX) "
        "и через пробел примерное время, необходимое на ремонт (в часах) "
        "(Необязатльное поле)",
    EditApplicationState.editing_app_notes:
        "Напишите допольнительную информацию, которую не удалось поместить в поля выше"
        "(Необязательное поле)",
}
