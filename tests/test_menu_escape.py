"""Menu buttons and /start must free an admin stuck in the photo state."""
import asyncio
from types import SimpleNamespace

from app.adapters.telegram.handlers import car_price, daily_prices, start
from app.adapters.telegram.texts import menu


class State:
    cleared = False

    async def clear(self):
        self.cleared = True


def _message(sent: list):
    async def answer(text, **kwargs):
        sent.append(text)
    return SimpleNamespace(
        text=menu.BTN_CAR_PRICE, chat=SimpleNamespace(id=1), answer=answer)


def test_start_clears_state():
    state = State()
    asyncio.run(start.on_start(_message([]), state))
    assert state.cleared


def test_car_price_clears_state(monkeypatch):
    monkeypatch.setattr(car_price.dbrun, "run", lambda *a: None)
    state = State()
    asyncio.run(car_price.on_car_price(_message([]), None, None, state))
    assert state.cleared


def test_menu_buttons_list():
    assert menu.BTN_CAR_PRICE in menu.MENU_BUTTONS
    # 3 menu buttons + old car price label + old my-car label (open keyboards).
    assert len(menu.MENU_BUTTONS) == 5


def test_photo_text_handler_still_registered():
    assert daily_prices.on_text is not None
