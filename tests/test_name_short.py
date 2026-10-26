from types import SimpleNamespace

from app.core import daily_cols
from app.core.name_short import short_name

TEXTS = SimpleNamespace(
    CHANGE_UP="▲{n}", CHANGE_DOWN="▼{n}", IMG_UP="▲{n}", IMG_DOWN="▼{n}",
    NO_VALUE="—",
)


def test_short_name_is_unchanged():
    assert short_name("پراید") == "پراید"


def test_brackets_are_dropped_first():
    assert short_name("چانگان CS35 پلاس مونتاژ (سایپا 421P)") == "چانگان CS35 پلاس مونتاژ"


def test_long_name_is_cut_at_word_edge():
    result = short_name("یک نام بسیار بسیار بسیار بلند برای آزمایش کوتاه کردن")
    assert result.endswith("\u2026") and len(result) <= 24


def test_only_bracket_name_is_still_cut():
    result = short_name("(" + "x" * 40 + ")")
    assert len(result) <= 24 and result.endswith("\u2026")


def test_cells_use_short_names():
    row = {"name": "چانگان CS35 پلاس مونتاژ (سایپا 421P)", "year": 1405,
           "price_m": 6500, "change_m": 0, "flags": []}
    assert daily_cols.cells([row], TEXTS)[0][0] == "چانگان CS35 پلاس مونتاژ"
