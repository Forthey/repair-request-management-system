from aiogram.fsm.context import FSMContext


async def back(state: FSMContext) -> bool:
    data = await state.get_data()
    old_state = data.get("__old_state")
    old_data = data.get("__old_data")

    await state.set_state(old_state)
    await state.set_data(old_data if old_data else {})

    return old_state is not None
