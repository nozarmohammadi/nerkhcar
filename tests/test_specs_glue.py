"""Tests for gluing years and units so they do not wrap alone."""
from app.core import specs_html

NBSP = "\u00a0"


def test_year_stays_with_word():
    out = specs_html.glue("نسل اول تولید از سال ۲۰۱۸")
    assert out.endswith("سال" + NBSP + "۲۰۱۸")


def test_number_stays_with_unit():
    assert specs_html.glue("۱۰۶۵ کیلوگرم") == "۱۰۶۵" + NBSP + "کیلوگرم"


def test_plain_text_untouched():
    assert specs_html.glue("هاچ‌بک") == "هاچ‌بک"
