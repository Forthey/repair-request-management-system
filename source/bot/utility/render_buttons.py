from aiogram.types import KeyboardButton, InlineKeyboardButton


def render_keyboard_buttons(item_list: list[any], num_in_row: int) -> list[list[KeyboardButton]]:
    buttons: list[list[KeyboardButton]] = list()
    for i in range(len(item_list)):
        if type(item_list[i // num_in_row]) is "list":
            buttons += render_keyboard_buttons(item_list[i], num_in_row)
        else:
            if i % num_in_row == 0:
                buttons.append([])
            buttons[i // num_in_row].append(KeyboardButton(text=item_list[i]))

    return buttons


def render_inline_buttons(item_list: list[any], num_in_row: int) -> list[list[InlineKeyboardButton]]:
    buttons: list[list[InlineKeyboardButton]] = list()
    for i in range(len(item_list)):
        if type(item_list[i // num_in_row]) is "list":
            buttons += render_inline_buttons(item_list[i], num_in_row)
        else:
            if i % num_in_row == 0:
                buttons.append([])
            buttons[i // num_in_row].append(InlineKeyboardButton(
                text=item_list[i],
                callback_data=item_list[i]
            ))

    return buttons
