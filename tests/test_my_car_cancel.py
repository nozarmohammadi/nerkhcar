import re
from pathlib import Path

from app.adapters.telegram.keyboards import my_car as k


def test_cancel_kb():
    rows = k.cancel_kb().inline_keyboard
    assert rows[0][0].callback_data == "mc:x"


def test_handler_keyboard_calls_exist():
    src = Path("app/adapters/telegram/handlers/my_car.py").read_text(encoding="utf-8")
    for name in set(re.findall(r"\bk\.(\w+)\(", src)):
        assert hasattr(k, name), name
