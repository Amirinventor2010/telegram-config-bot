from aiogram.fsm.state import StatesGroup, State


class AddConfigState(StatesGroup):
    waiting_for_link = State()
