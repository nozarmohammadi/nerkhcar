"""States and screens of the 'my car' form (no routes here)."""
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from app.adapters.telegram.keyboards import my_car as k
from app.adapters.telegram.texts import my_car as t
from app.core import daily_text, model_lookup, used_base_auto
from app.core import my_car_options as opt


class MyCar(StatesGroup):
    model = State()
    year = State()
    km = State()
    body = State()
    chassis = State()


PREV = {"year": "model", "km": "year", "body": "km", "chassis": "body"}
CHOICES = {
    "km": (t.ASK_KM, "k", t.KM_LABELS),
    "body": (t.ASK_BODY, "b", t.BODY_LABELS),
    "chassis": (t.ASK_CHASSIS, "c", t.CHASSIS_LABELS),
}


def screen(step: str, data: dict):
    """Return (text, keyboard) of one step of the form."""
    if step == "model":
        names, page = data["names"], data.get("page", 0)
        text = t.ASK_MODEL.format(
            page=daily_text.fa(page + 1),
            pages=daily_text.fa(model_lookup.page_count(names)))
        return text, k.models_kb(names, page)
    if step == "year":
        current = used_base_auto.current_year(datetime.now())
        return t.ASK_YEAR, k.years_kb(opt.year_choices(current))
    text, kind, labels = CHOICES[step]
    return text, k.choice_kb(kind, labels)


async def show(cb: CallbackQuery, state: FSMContext, step: str) -> None:
    """Move the form to a step and redraw the message."""
    text, kb = screen(step, await state.get_data())
    await state.set_state(getattr(MyCar, step))
    await cb.message.edit_text(text, reply_markup=kb)
