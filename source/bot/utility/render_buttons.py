from aiogram.types import KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def render_keyboard_buttons(item_list: list[str], num_in_row: int) -> ReplyKeyboardMarkup:
    buttons: list[list[KeyboardButton]] = list()
    for i in range(len(item_list)):
        if i % num_in_row == 0:
            buttons.append([])
        buttons[i // num_in_row].append(KeyboardButton(text=item_list[i]))

    return ReplyKeyboardMarkup(keyboard=buttons)


def render_inline_buttons(item_list: dict[str, str], num_in_row: int) -> InlineKeyboardMarkup:
    buttons: list[list[InlineKeyboardButton]] = list()
    i = 0
    for key in item_list:
        if i % num_in_row == 0:
            buttons.append([])
        buttons[i // num_in_row].append(InlineKeyboardButton(
            text=item_list[key],
            callback_data=key
        ))

    return InlineKeyboardBuilder(buttons).as_markup()
