"""States and screens of the typed 'my car' form (no routes here)."""
from aiogram.fsm.state import State, StatesGroup

from app.adapters.telegram.keyboards import my_car as k
from app.adapters.telegram.texts import my_car as t


class MyCar(StatesGroup):
    name = State()
    pick = State()
    year = State()
    km = State()
    body = State()
    chassis = State()


def choice_screen(step: str):
    """Text and keyboard of a button step (body or chassis)."""
    if step == "body":
        return t.ASK_BODY, k.choice_kb("b", t.BODY_LABELS)
    return t.ASK_CHASSIS, k.choice_kb("c", t.CHASSIS_LABELS)


def pick_screen(found: list[str]):
    return t.PICK_NAME, k.names_kb(found)
