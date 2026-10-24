"""تست خواندن جدول از عکس (با پاسخ‌های ساختگی؛ بدون شبکه)."""
import asyncio

from app.adapters.ai import gemini
from app.config import Settings
from app.core import table_parse, table_read

FENCE = "`" * 3


def test_to_int_variants():
    assert table_parse.to_int("۱/۵۸۰/۰۰۰/۰۰۰") == 1580000000
    assert table_parse.to_int("١٢٣") == 123
    assert table_parse.to_int("-5") == -5
    assert table_parse.to_int(12.0) == 12
    assert table_parse.to_int(None) is None
    assert table_parse.to_int(True) is None
    assert table_parse.to_int("abc") is None
    assert table_parse.to_int(float("nan")) is None


def test_parse_response_variants():
    fenced = f'{FENCE}json\n[{{"name": "x"}}]\n{FENCE}'
    assert table_parse.parse_response(fenced) == [{"name": "x"}]
    wrapped = '{"rows": [{"name": "x"}]}'
    assert table_parse.parse_response(wrapped) == [{"name": "x"}]
    assert table_parse.parse_response("not json") is None
    assert table_parse.parse_response("[]") is None
    assert table_parse.parse_response('{"a": 1}') is None


def test_normalize_good_row():
    raw = {"name": "ساینا اس", "year": 1405, "price": 1720000000,
           "change": 15000000, "note": ""}
    row = table_parse.normalize_row(raw)
    assert row == {"name": "ساینا اس", "year": 1405, "price_m": 1720,
                   "change_m": 15, "flags": []}
    text_price = dict(raw, price="۱/۵۸۰/۰۰۰/۰۰۰")
    assert table_parse.normalize_row(text_price)["price_m"] == 1580


def test_empty_price_flagged():
    row = table_parse.normalize_row(
        {"name": "ساینا اتومات", "year": 1405, "price": None, "change": None})
    assert row["price_m"] is None and "no_price" in row["flags"]


def test_year_flags():
    base = {"name": "a", "price": 1720000000}
    assert table_parse.normalize_row(dict(base, year=1405))["flags"] == []
    assert "greg_year" in table_parse.normalize_row(dict(base, year=2025))["flags"]
    assert "bad_year" in table_parse.normalize_row(dict(base, year=14))["flags"]
    assert "no_year" in table_parse.normalize_row(dict(base))["flags"]


def test_rounded_and_range_flags():
    base = {"name": "a", "year": 1405}
    rounded = table_parse.normalize_row(dict(base, price=1920400000))
    assert rounded["price_m"] == 1920 and "rounded" in rounded["flags"]
    small = table_parse.normalize_row(dict(base, price=5000000))
    assert small["price_m"] == 5 and "range" in small["flags"]
    assert "rounded" not in small["flags"]


def test_note_merged_and_long_name_cut():
    row = table_parse.normalize_row(
        {"name": "چانگان cs35 خاکستری", "note": "مونتاژی", "year": 1405,
         "price": 6350000000})
    assert row["name"] == "چانگان cs35 خاکستری مونتاژی"
    long_row = table_parse.normalize_row({"name": "الف" * 50, "year": 1405})
    assert len(long_row["name"]) == 40 and "long_name" in long_row["flags"]


def test_non_dict_row_marked_bad():
    rows = table_parse.normalize_rows(["x"])
    assert len(rows) == 1 and rows[0]["flags"] == ["bad_row"]


def test_read_table_uses_fallback():
    calls = []
    good = '[{"name": "ساینا اس", "year": 1405, "price": 1720000000}]'

    async def fake(image, mime, model):
        calls.append(model)
        return ("rate_limit", "") if model == "m1" else ("ok", good)

    status, rows = asyncio.run(
        table_read.read_table(fake, b"x", "image/jpeg", ("m1", "m2")))
    assert status == "ok" and calls == ["m1", "m2"]
    assert rows[0]["price_m"] == 1720


def test_read_table_all_fail():
    async def down(image, mime, model):
        return "http_500", ""

    async def garbage(image, mime, model):
        return "ok", "not json"

    models = ("m1", "m2")
    assert asyncio.run(table_read.read_table(down, b"x", "image/png", models)) == (
        "http_500", [])
    assert asyncio.run(table_read.read_table(garbage, b"x", "image/png", models)) == (
        "bad_reply", [])
    assert asyncio.run(table_read.read_table(down, b"x", "image/png", ())) == (
        "no_model", [])


def test_gemini_helpers():
    body = gemini.build_body(b"abc", "image/jpeg")
    part = body["contents"][0]["parts"][1]["inline_data"]
    assert part["mime_type"] == "image/jpeg" and part["data"] == "YWJj"
    assert body["generationConfig"]["temperature"] == 0
    good = {"candidates": [{"content": {"parts": [{"text": "[1]"}, {"text": "2"}]}}]}
    assert gemini.reply_text(good) == "[1]2"
    assert gemini.reply_text({}) == ""
    assert gemini._result(429, {}) == ("rate_limit", "")
    assert gemini._result(500, {}) == ("http_500", "")
    assert gemini._result(200, {}) == ("empty", "")
    assert gemini._result(200, good) == ("ok", "[1]2")


def test_settings_defaults_and_hidden_key(tmp_path):
    plain = Settings("tok", 7, tmp_path / "a.db", tmp_path)
    assert plain.gemini_key == "" and len(plain.vision_models) == 2
    keyed = Settings("tok", 7, tmp_path / "a.db", tmp_path, gemini_key="abc123")
    assert "abc123" not in repr(keyed)
