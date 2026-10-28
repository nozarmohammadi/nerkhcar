"""Tests for the hamrah-mechanic page parser."""
import json

from app.core import hm_parse


def _page(props) -> str:
    data = {"props": {"pageProps": props}}
    return ('<html><script id="__NEXT_DATA__" type="application/json">'
            + json.dumps(data, ensure_ascii=False) + "</script></html>")


def _item(year, price, type_name="Glx"):
    return {"brandName": "ایران خودرو", "modelName": "پژو 405",
            "carTypeName": type_name, "carYear": year, "marketPrice": price}


def test_page_props_missing_or_broken():
    assert hm_parse.page_props("<html></html>") is None
    broken = '<script id="__NEXT_DATA__">{oops</script>'
    assert hm_parse.page_props(broken) is None


def test_model_slugs_found_anywhere():
    props = {"a": [{"x": {"modelEnglishName": "peugeot405",
                          "modelName": "پژو 405"}}]}
    assert hm_parse.model_slugs(props) == {"peugeot405": "پژو 405"}


def test_year_rows_shape_and_order():
    items = [_item(1398, 1_230_000_000), _item(1399, 1_330_000_000)]
    props = hm_parse.page_props(_page(
        {"yearsPriceList": {"carPriceOtherYearsDetails": items}}))
    rows = hm_parse.year_rows(props)
    assert [r["year"] for r in rows] == [1399, 1398]
    assert rows[0] == {
        "name": "پژو 405 Glx", "year": 1399, "price_m": 1330,
        "change_m": None, "brand": "ایران خودرو", "flags": []}


def test_gregorian_year_is_converted_and_bad_rows_skipped():
    items = [_item(2024, 8_000_000_000), _item(1500 + 900, 5),
             _item(1399, 0), _item(1399, None), _item(None, 5)]
    rows = hm_parse.year_rows(
        {"yearsPriceList": {"carPriceOtherYearsDetails": items}})
    assert [(r["year"], r["price_m"]) for r in rows] == [(1403, 8000)]


def test_empty_props_give_no_rows():
    assert hm_parse.year_rows({}) == []
