from app.adapters.telegram.keyboards import my_car as k
from app.adapters.telegram.texts import my_car as t


def datas(kb):
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def test_models_first_page():
    kb = k.models_kb([str(i) for i in range(20)], 0)
    d = datas(kb)
    assert d[0] == "mc:m:0" and "mc:p:1" in d and "mc:p:-1" not in d
    assert d[-1] == "mc:x"


def test_models_last_page_has_prev_only():
    d = datas(k.models_kb([str(i) for i in range(20)], 2))
    assert "mc:p:1" in d and "mc:p:3" not in d


def test_years_and_choices():
    assert "mc:y:1405" in datas(k.years_kb([1405, 1404]))
    d = datas(k.choice_kb("k", t.KM_LABELS))
    assert d[:2] == ["mc:k:0", "mc:k:1"] and "mc:back" in d


def test_callback_short():
    for d in datas(k.models_kb([str(i) for i in range(99)], 3)):
        assert len(d.encode()) <= 64
