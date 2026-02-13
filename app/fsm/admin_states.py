from aiogram.fsm.state import StatesGroup, State


class AddConfigState(StatesGroup):
    waiting_for_v2ray = State()
