"""Zoomit specs parser: labels, stop marker, cylinder/valve fix."""
from app.core import car_specs_parse as p

REV = {v: k for k, v in p.LABELS.items()}


def _text(pairs):
    lines = ["nav junk", p.START]
    for key, value in pairs:
        lines += [REV[key], value]
    lines += [p.STOP, REV["power"], "9999"]
    return "\n".join(lines)


def test_basic_and_stop_marker():
    out = p.parse_zoomit_text(_text([("displacement", "1481"), ("power", "195 hp")]))
    assert out["displacement"] == "1481"
    assert out["power"] == "195 hp"


def test_cylinders_valves_swapped():
    out = p.parse_zoomit_text(_text([("cylinders", "16"), ("valves", "4")]))
    assert out["cylinders"] == "4"
    assert out["valves"] == "16"
    assert out["note"] == "cylinders_valves_swapped"


def test_normal_cylinders_untouched():
    out = p.parse_zoomit_text(_text([("cylinders", "4"), ("valves", "16")]))
    assert out["cylinders"] == "4"
    assert "note" not in out


def test_multiline_value_joined():
    out = p.parse_zoomit_text(_text([("series", "first\nsecond")]))
    assert out["series"] == "first second"


def test_missing_start_returns_empty():
    assert p.parse_zoomit_text("nothing here") == {}


def test_html_to_text_drops_scripts():
    text = p.html_to_text("<p>a</p><script>var x</script><b>b</b>")
    assert "var x" not in text
    assert "a" in text and "b" in text


def test_zwnj_kept_in_values():
    value = "285 نیوتن\u200cمتر"
    out = p.parse_zoomit_text(_text([("torque", value)]))
    assert out["torque"] == value


def test_cvt_label_not_merged_into_gearbox():
    out = p.parse_zoomit_text(_text([("gearbox", "manual"), ("cvt", "no")]))
    assert out["gearbox"] == "manual"
    assert out["cvt"] == "no"
