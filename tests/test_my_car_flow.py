from app.adapters.telegram.handlers import my_car_flow as f


def datas(kb):
    return [b.callback_data for row in kb.inline_keyboard for b in row]


def test_pick_screen():
    _, kb = f.pick_screen(["a", "b"])
    assert datas(kb)[:2] == ["mc:m:0", "mc:m:1"]


def test_choice_screens():
    _, kb = f.choice_screen("body")
    assert datas(kb)[0] == "mc:b:0" and "mc:back" in datas(kb)
    _, kb = f.choice_screen("chassis")
    assert datas(kb)[0] == "mc:c:0"
