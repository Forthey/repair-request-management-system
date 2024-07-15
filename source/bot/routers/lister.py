from typing import Callable, Awaitable, Any

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.states.lister import ListerState
from bot.utility.render_buttons import render_inline_buttons


router = Router()


class Lister[Schema]:
    _list_commands = {
        "next_chunk": "Далее",
        "prev_chunk": "Назад",
    }
    _offset = 0
    _max_offset = 0
    _chunk_size = 0
    _filters: dict = {}
    _get_func: Callable[..., Awaitable[list[Schema]]]
    _result_to_str_func: Callable[..., str]

    async def _init(
            self,
            get_func: Callable[..., Awaitable[list[Schema]]],
            count_func: Callable[..., Awaitable[int]],
            result_to_str_func: Callable[[list[Schema]], str],
            message: Message, state: FSMContext,
            chunk_size=3, offset=0,
            **filters):
        self._offset = offset
        self._max_offset = await count_func(**filters)
        self._chunk_size = chunk_size
        self._filters = filters
        self._get_func = get_func
        self._result_to_str_func = result_to_str_func

        await state.update_data(lister=self)

        first_result: list[Schema] = await self.get()
        await message.answer(
            self._result_to_str_func(first_result),
            reply_markup=render_inline_buttons(self._list_commands, 2)
        )
        await state.set_state(ListerState.listing)

    async def get(self) -> list[Schema]:
        return await self._get_func(self._offset, self._chunk_size, **self._filters)

    def change_page(self, value: int) -> bool:
        new_offset = self._offset + value * self._chunk_size
        if not (0 <= new_offset < self._max_offset):
            return False
        self._offset = new_offset
        return True

    @staticmethod
    @router.callback_query(StateFilter(ListerState.listing), F.data == "next_chunk")
    @router.callback_query(StateFilter(ListerState.listing), F.data == "prev_chunk")
    async def change_page_callback[Schema](query: CallbackQuery, state: FSMContext):
        value = 1 if query.data == "next_chunk" else -1
        lister: Lister | None = (await state.get_data()).get("lister")
        if not lister:
            await query.answer("Что-то пошло не так...")
            return
        if not lister.change_page(value):
            await query.answer("Это крайняя страница")
            return
        await state.update_data(lister=lister)

        chunk_result: list[Schema] = await lister.get()
        await query.message.edit_text(
            lister._result_to_str_func(chunk_result),
            reply_markup=render_inline_buttons(lister._list_commands, 3)
        )


async def create_lister[Schema](
        get_func: Callable[..., Awaitable[list[Schema]]],
        count_func: Callable[..., Awaitable[int]],
        result_to_str_func: Callable[[list[Schema]], str],
        message: Message, state: FSMContext,
        chunk_size=3, offset=0,
        **filters) -> Lister:
    lister = Lister()
    await lister._init(get_func, count_func, result_to_str_func, message, state, chunk_size, offset, **filters)
    return lister
