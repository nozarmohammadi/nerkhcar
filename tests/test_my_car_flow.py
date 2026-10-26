from app.adapters.telegram.handlers import my_car_flow as f
from app.core import daily_text


def datas(kb):
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def test_model_screen():
    text, kb = f.screen("model", {"names": ["a", "b"], "page": 0})
    assert daily_text.fa(1) in text and datas(kb)[0] == "mc:m:0"


def test_year_screen():
    _, kb = f.screen("year", {})
    assert datas(kb)[0].startswith("mc:y:14")


def test_choice_screens():
    for step, kind in (("km", "k"), ("body", "b"), ("chassis", "c")):
        _, kb = f.screen(step, {})
        assert datas(kb)[0] == f"mc:{kind}:0"


def test_prev_chain():
    assert f.PREV["chassis"] == "body" and "model" not in f.PREV
