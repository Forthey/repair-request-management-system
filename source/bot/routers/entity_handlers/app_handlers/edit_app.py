from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from bot.state_watchers.application import EditApplicationState
from bot.utility.render_buttons import render_inline_buttons, render_keyboard_buttons


edit_field = {
    "edit_contact": "Контакт",
    "edit_reasons": "Причины",
    "edit_machine": "Станок",
    "edit_address": "Адрес",
    "edit_est_rep_date": "Дата ремонта",
    "edit_est_duration": "Время ремонта",
    "edit_app_confitm": "Подвердить",
}


router = Router()


@router.message(StateFilter(None), F.text.lower() == "изменить заявку")
async def edit_app(message: Message, state: FSMContext):
    await message.answer("Введите id заявки")
    await state.set_state(EditApplicationState.choosing_app_id)


@router.message(StateFilter(EditApplicationState.choosing_app_id))
async def getting_app_from_id(message: Message, state: FSMContext):
    pass
