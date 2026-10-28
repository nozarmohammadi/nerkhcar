"""Tests for the hamrah-mechanic downloader (network replaced by a fake)."""
import asyncio

from app.adapters import hm_fetch

BRAND = {"x": [{"modelEnglishName": "m1", "modelName": "M1"},
               {"modelEnglishName": "m2", "modelName": "M2"}]}


def _model(name):
    item = {"brandName": "b", "modelName": name, "carTypeName": "",
            "carYear": 1399, "marketPrice": 1_000_000_000}
    return {"yearsPriceList": {"carPriceOtherYearsDetails": [item]}}


def _fake(pages):
    async def props(session, path):
        return pages.get(path)
    return props


def test_only_missing_models_are_fetched(monkeypatch):
    pages = {"irankhodro/": BRAND, "irankhodro/m1/": _model("M1"),
             "irankhodro/m2/": _model("M2")}
    monkeypatch.setattr(hm_fetch, "_props", _fake(pages))
    monkeypatch.setattr(hm_fetch, "PAUSE", 0)
    rows = asyncio.run(hm_fetch.fetch_missing_rows(["m2 x"]))
    assert [r["name"] for r in rows] == ["M1"]


def test_failed_pages_give_no_rows(monkeypatch):
    monkeypatch.setattr(hm_fetch, "_props", _fake({}))
    monkeypatch.setattr(hm_fetch, "PAUSE", 0)
    assert asyncio.run(hm_fetch.fetch_missing_rows([])) == []


def test_slug_is_fetched_once_across_brands(monkeypatch):
    pages = {"irankhodro/": BRAND, "saipa/": BRAND,
             "irankhodro/m1/": _model("M1"), "irankhodro/m2/": _model("M2"),
             "saipa/m1/": _model("M1"), "saipa/m2/": _model("M2")}
    monkeypatch.setattr(hm_fetch, "_props", _fake(pages))
    monkeypatch.setattr(hm_fetch, "PAUSE", 0)
    rows = asyncio.run(hm_fetch.fetch_missing_rows([]))
    assert len(rows) == 2
