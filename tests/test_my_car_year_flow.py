import asyncio
from types import SimpleNamespace

from app.adapters.telegram.handlers import my_car
from app.adapters.telegram.texts import my_car as t


class Msg:
    def __init__(self, text):
        self.text = text
        self.sent = []

    async def answer(self, text, **kw):
        self.sent.append(text)


class State:
    def __init__(self, data):
        self.data = dict(data)
        self.state = None

    async def get_data(self):
        return self.data

    async def update_data(self, **kw):
        self.data.update(kw)

    async def set_state(self, s):
        self.state = s


def test_single_result_goes_to_year():
    st = State({"names": ["آریسان 2", "اطلس"]})
    msg = Msg("آریسان")
    asyncio.run(my_car.on_name(msg, st))
    assert st.data["name"] == "آریسان 2"
    assert msg.sent == [t.ASK_YEAR_TYPED]


def test_year_after_last(monkeypatch):
    pub = {"rows": [{"name": "A", "year": 1403, "price_m": 1}]}
    monkeypatch.setattr(my_car.dbrun, "run", lambda *a: pub)
    st = State({"name": "A"})
    msg = Msg("1405")
    asyncio.run(my_car.on_year(msg, st, SimpleNamespace()))
    assert "year" not in st.data
    assert "۱۴۰۳" in msg.sent[0]


def test_year_ok(monkeypatch):
    pub = {"rows": [{"name": "A", "year": 1403, "price_m": 1}]}
    monkeypatch.setattr(my_car.dbrun, "run", lambda *a: pub)
    st = State({"name": "A"})
    msg = Msg("1402")
    asyncio.run(my_car.on_year(msg, st, SimpleNamespace()))
    assert st.data["year"] == 1402 and msg.sent == [t.ASK_KM_TYPED]
