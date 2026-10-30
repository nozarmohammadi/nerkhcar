import json
from pathlib import Path

from app.core.specs_html import compact

CFG = json.loads(Path("app/data/spec_shorten.json").read_text(encoding="utf-8"))


def test_unit_moves_to_label():
    unit = CFG["units"][0]
    out = compact([("x", f"1465 \u00d7 1720 \u00d7 4680 {unit}")])
    assert out == [(f"x ({unit})", "1465\u00d71720\u00d74680")]


def test_series_is_short():
    sep, join = CFG["series_sep"], CFG["series_join"]
    assert compact([("s", f"A{sep}2022")]) == [("s", f"A{join}2022")]


def test_plain_value_untouched():
    assert compact([("k", "plain")]) == [("k", "plain")]
