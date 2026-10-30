"""Specs detail keyboard and price footer under the table."""
from app.adapters.telegram.keyboards import specs as k
from app.adapters.telegram.texts import specs as t
from app.core import specs_html


def test_detail_kb_no_price_button():
    kb = k.detail_kb(42)
    texts = [b.text for row in kb.inline_keyboard for b in row]
    assert t.BTN_CHART in texts
    assert t.BTN_COMPARE in texts
    assert t.BTN_HOME in texts
    assert all("قیمت امروز" not in x for x in texts)
    data = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert "spec:chart:42" in data
    assert "spec:compare:42" in data
    assert "spec:home" in data
    assert not any(d.startswith("spec:p:") for d in data)


def test_chart_compare_texts():
    assert "به‌زودی" in t.CHART_SOON
    assert "به‌زودی" in t.COMPARE_SOON


def test_price_footer_templates():
    # fresh: no "امروز" in header, no date line
    assert "امروز" not in t.PRICE_HEADER
    assert "مربوط به" in t.OLD_DATE_LINE
    assert "موجود نیست" in t.NO_PRICE


def test_build_text_includes_price():
    text = specs_html.build_text("T", [("a", "1")], price="💰 قیمت خودرو\nمدل")
    assert "💰 قیمت خودرو" in text


def test_build_html_includes_price():
    html = specs_html.build_html("T", [("a", "1")], ("x", "y"), price="p1\np2")
    assert "p1" in html and "p2" in html
