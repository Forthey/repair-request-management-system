from types import NoneType

from aiogram import Router, F
from aiogram.filters import BaseFilter, StateFilter
from aiogram.types import Message

from bot.routers.new_handlers import (
    new_command_menu,
    add_client,
    add_machine,
    add_company_position,
    add_company_activity,
    add_close_reason,
    error
)


# This scope filter
class NewFilter(BaseFilter):  # [1]
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:  # [3]
        args = message.text.split(" ")
        if args[0].lower() != "/new":
            return False
        return True


# Router
router = Router()
router.message.filter(
    F.text,
    NewFilter()
)

# Include sub routers
router.include_routers(
    new_command_menu.router,
    add_client.router,
    add_machine.router,
    add_company_position.router,
    add_close_reason.router,
    add_company_activity.router,
    error.router
)
