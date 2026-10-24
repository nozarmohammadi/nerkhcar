"""FSM states of the daily-prices flow."""
from aiogram.fsm.state import State, StatesGroup


class Daily(StatesGroup):
    photos = State()
