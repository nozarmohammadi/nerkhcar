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


def test_glued_tail_is_cut():
    marker = CFG["cut_at"][0]
    assert compact([("k", f"abc {marker} xyz")]) == [("k", "abc")]


def test_rpm_is_short():
    key, sep = CFG["rpm_keys"][0], CFG["rpm_sep"]
    out = compact([(key, f"104{sep}5500{CFG['rpm_in']}")])
    assert out[0][1] == "104 (5500" + CFG["rpm_out"][:-1] + ")"
