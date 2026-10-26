from app.adapters.telegram.keyboards import my_car as k
from app.adapters.telegram.texts import my_car as t


def datas(kb):
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def test_names_kb():
    d = datas(k.names_kb(["a", "b"]))
    assert d == ["mc:m:0", "mc:m:1", "mc:x"]


def test_choice_kb():
    d = datas(k.choice_kb("k", t.KM_LABELS))
    assert d[:2] == ["mc:k:0", "mc:k:1"] and "mc:back" in d
