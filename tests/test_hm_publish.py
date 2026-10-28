"""Tests for publishing 1car rows together with the extra models."""
import asyncio

from app.core import hm_merge
from app.jobs import car_price_job as job


_FORCED = []


def _wire(monkeypatch, fetcher):
    calls = []
    forced = _FORCED
    forced.clear()
    monkeypatch.setattr(job.pub, "auto_rows", lambda html: [{"name": "دنا پلاس"}])
    monkeypatch.setattr(job.hm_fetch, "fetch_missing_rows", fetcher)

    def fake_publish(settings, html, moment=None, extra=None, force=False):
        calls.append(extra)
        forced.append(force)
        return True

    monkeypatch.setattr(job, "publish_auto", fake_publish)
    return calls


def test_publish_full_passes_extra_rows(monkeypatch):
    seen = []

    async def fetcher(ours):
        seen.append(ours)
        return [{"name": "x", "year": 1, "price_m": 500}]

    calls = _wire(monkeypatch, fetcher)
    assert asyncio.run(job.publish_full(None, "h")) is True
    assert seen == [["دنا پلاس"]] and calls[0][0]["name"] == "x"


def test_publish_full_survives_hm_failure(monkeypatch):
    async def fetcher(ours):
        raise RuntimeError("down")

    calls = _wire(monkeypatch, fetcher)
    assert asyncio.run(job.publish_full(None, "h")) is True
    assert calls == [[]]


def test_valid_filters_price_range():
    rows = [{"price_m": 50}, {"price_m": 500}, {"price_m": 10**7}]
    assert hm_merge.valid(rows) == [{"price_m": 500}]


def test_publish_full_passes_force(monkeypatch):
    async def fetcher(ours):
        return []

    _wire(monkeypatch, fetcher)
    assert asyncio.run(job.publish_full(None, "h", force=True)) is True
    assert _FORCED == [True]
