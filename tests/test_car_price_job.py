"""Tests for the daily car price schedule and job (no network)."""
import asyncio
from datetime import datetime

from app.adapters import car_price_fetch as f
from app.core import car_price_schedule as s
from app.jobs import car_price_job as job

TODAY = "1405-08-03"


def _patch(monkeypatch, html):
    async def fake():
        return html
    saved = []
    monkeypatch.setattr(f, "fetch_page", fake)
    monkeypatch.setattr(f, "save_raw", lambda h: saved.append(h))
    return saved


def test_jalali_day():
    assert s.jalali_day(datetime(2026, 10, 25, 14, 0)) == TODAY


def test_window():
    assert s.in_window(datetime(2026, 10, 25, 14, 0))
    assert not s.in_window(datetime(2026, 10, 25, 8, 59))
    assert not s.in_window(datetime(2026, 10, 25, 18, 0))
    assert not s.in_window(datetime(2026, 10, 30, 14, 0))  # Friday


def test_run_once_fresh(monkeypatch):
    saved = _patch(monkeypatch, f'"dateModified": "{TODAY}"')
    assert asyncio.run(job.run_once(TODAY)) == "fresh"
    assert len(saved) == 1


def test_run_once_old(monkeypatch):
    saved = _patch(monkeypatch, '"dateModified": "1405-08-02"')
    assert asyncio.run(job.run_once(TODAY)) == "old"
    assert saved == []


def test_run_once_fail(monkeypatch):
    _patch(monkeypatch, None)
    assert asyncio.run(job.run_once(TODAY)) == "fail"


def test_already_saved(monkeypatch, tmp_path):
    monkeypatch.setattr(f, "RAW_DIR", tmp_path)
    assert not job.already_saved(TODAY)
    (tmp_path / f"price-{TODAY}.html").write_text("x")
    assert job.already_saved(TODAY)
