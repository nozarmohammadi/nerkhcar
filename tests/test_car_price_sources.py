"""Independent daily sources: 1car and hamrah-mechanic (no network)."""
import asyncio
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from app.core import car_price_sources as src
from app.jobs import car_price_job as job

TEHRAN = ZoneInfo("Asia/Tehran")
DAY = "1405-08-03"
SETTINGS = SimpleNamespace(owner_id=7)
ONE = ["دنا", "پژو"]
HM_ROWS = [
    {"name": "دنا", "year": 1404, "price_m": 500},
    {"name": "تارا", "year": 1404, "price_m": 600},
]


class Env:
    """Fake network: switch each source on or off and record what happens."""

    def __init__(self, monkeypatch):
        self.one_ok = self.hm_ok = self.saved = False
        self.one_calls = self.hm_calls = 0
        self.published = []
        monkeypatch.setattr(job, "run_once", self._run_once)
        monkeypatch.setattr(job, "already_saved", lambda d: self.saved)
        monkeypatch.setattr(job, "_onecar_html", lambda d: "h" if self.saved else None)
        monkeypatch.setattr(src, "names", lambda h: ONE if h else [])
        monkeypatch.setattr(job.hm_fetch, "fetch_missing_rows", self._hm)
        monkeypatch.setattr(job, "publish_auto", self._publish)

    async def _run_once(self, today, on_fresh=None):
        self.one_calls += 1
        self.saved = self.saved or self.one_ok
        return "fresh" if self.one_ok else "fail"

    async def _hm(self, ours):
        self.hm_calls += 1
        return list(HM_ROWS) if self.hm_ok else []

    def _publish(self, settings, html, moment=None, extra=None, force=False):
        self.published.append((html, [r["name"] for r in (extra or [])]))
        return True


def slot(state, hour, minute, sec=5):
    now = datetime(2026, 10, 25, hour, minute, sec, tzinfo=TEHRAN)
    asyncio.run(job._round(SETTINGS, DAY, now, state))


def test_onecar_ok_then_hm_keeps_trying(monkeypatch):
    env, st = Env(monkeypatch), src.new_state()
    env.one_ok = True
    slot(st, 11, 30)
    assert st["done"] == {src.ONECAR} and env.published == [("h", [])]
    slot(st, 12, 30)
    assert env.one_calls == 1 and env.hm_calls == 2
    env.hm_ok = True
    slot(st, 13, 30)
    assert st["done"] == {src.ONECAR, src.HM}
    assert env.published[-1] == ("h", ["تارا"])


def test_hm_ok_then_onecar_keeps_trying(monkeypatch):
    env, st = Env(monkeypatch), src.new_state()
    env.hm_ok = True
    slot(st, 11, 30)
    assert st["done"] == {src.HM} and env.published == []
    slot(st, 12, 30)
    assert env.one_calls == 2 and env.hm_calls == 1
    env.one_ok = True
    slot(st, 13, 30)
    assert env.published == [("h", ["تارا"])]


def test_hm_full_fallback_only_after_final(monkeypatch):
    env, st = Env(monkeypatch), src.new_state()
    env.hm_ok = True
    for hour in (11, 12, 13):
        slot(st, hour, 30)
    assert env.published == []
    slot(st, 14, 30)
    assert env.published == [(None, ["دنا", "تارا"])]
    assert env.one_calls == 4


def test_hm_failure_keeps_valid_onecar_rows(monkeypatch):
    env, st = Env(monkeypatch), src.new_state()
    env.one_ok = True
    for hour in (11, 12, 13, 14):
        slot(st, hour, 30)
    assert env.published == [("h", [])]
    assert env.hm_calls == 4


def test_failed_sources_publish_nothing_old(monkeypatch):
    env, st = Env(monkeypatch), src.new_state()
    for hour in (11, 12, 13, 14):
        slot(st, hour, 30)
    assert env.published == []


def test_both_done_ends_the_day(monkeypatch):
    env, st = Env(monkeypatch), src.new_state()
    env.one_ok = env.hm_ok = True
    slot(st, 11, 30)
    assert st["done"] == {src.ONECAR, src.HM} and len(env.published) == 1
    slot(st, 12, 30)
    slot(st, 13, 30)
    assert (env.one_calls, env.hm_calls, len(env.published)) == (1, 1, 1)


def test_no_attempt_after_final_and_once_per_slot(monkeypatch):
    env, st = Env(monkeypatch), src.new_state()
    slot(st, 14, 30)
    slot(st, 14, 35)
    slot(st, 14, 55)
    slot(st, 16, 0)
    assert env.one_calls == 1


def test_new_day_drops_old_source_state():
    st = src.new_state()
    st.update(day="1405-08-02", done={src.ONECAR, src.HM}, pub="full")
    st["hm_rows"] = list(HM_ROWS)
    src.roll(st, DAY)
    assert st["day"] == DAY and st["done"] == set()
    assert st["hm_rows"] == [] and st["pub"] is None


def test_extra_rows_adds_only_missing_models():
    assert [r["name"] for r in src.extra_rows(ONE, HM_ROWS)] == ["تارا"]


def test_extra_rows_without_onecar_keeps_all():
    assert src.extra_rows([], HM_ROWS) == HM_ROWS


def test_plan_table():
    st = src.new_state()
    assert src.plan(st, True) is None
    st["done"] = {src.HM}
    assert src.plan(st, False) is None and src.plan(st, True) == "hm"
    st["done"] = {src.ONECAR}
    assert src.plan(st, False) == "onecar"
    st["done"] = {src.ONECAR, src.HM}
    assert src.plan(st, False) == "full"


def test_startup_publish_still_forces(monkeypatch, tmp_path):
    (tmp_path / "price-x.html").write_text("html", encoding="utf-8")
    monkeypatch.setattr(job.fetch, "RAW_DIR", tmp_path)
    calls = []

    async def fake_full(settings, html, moment=None, force=False):
        calls.append((html, force))
        return True

    monkeypatch.setattr(job, "publish_full", fake_full)
    asyncio.run(job.publish_latest(SETTINGS))
    assert calls == [("html", True)]
