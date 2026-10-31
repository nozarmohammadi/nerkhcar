"""FX background job: errors never stop it and data stays under 10 minutes old."""
import asyncio
from pathlib import Path

import pytest

from app.adapters.telegram import fx_refresh
from app.core import fx_view
from app.jobs import fx_job

MAIN = Path(__file__).resolve().parent.parent / "app" / "main.py"


class _Stop(Exception):
    pass


def test_round_refreshes_once(monkeypatch):
    calls = []

    async def fake(settings):
        calls.append(settings)
        return []

    monkeypatch.setattr(fx_refresh, "get_rows", fake)
    assert asyncio.run(fx_job.run_round("s")) is True
    assert calls == ["s"]


def test_round_swallows_errors(monkeypatch):
    async def boom(settings):
        raise RuntimeError("x")

    monkeypatch.setattr(fx_refresh, "get_rows", boom)
    assert asyncio.run(fx_job.run_round("s")) is False


def test_loop_sleeps_interval_between_rounds(monkeypatch):
    slept = []

    async def fake(settings):
        return []

    async def stop(seconds):
        slept.append(seconds)
        raise _Stop

    monkeypatch.setattr(fx_refresh, "get_rows", fake)
    monkeypatch.setattr(fx_job.asyncio, "sleep", stop)
    with pytest.raises(_Stop):
        asyncio.run(fx_job.loop("s"))
    assert slept == [fx_job.INTERVAL]


def test_interval_keeps_data_under_ten_minutes():
    stale = fx_view.MAX_AGE_MIN * 60
    assert stale <= fx_job.INTERVAL
    assert fx_job.INTERVAL + stale <= 600


def test_main_starts_the_job():
    assert "fx_job.loop(settings)" in MAIN.read_text(encoding="utf-8")
