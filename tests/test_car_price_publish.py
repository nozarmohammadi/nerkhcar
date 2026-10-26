"""Tests for auto-publishing the 1car.ir table (no network)."""
import asyncio
from datetime import datetime, timezone

from app.adapters import car_price_fetch as f
from app.core import car_price_publish as pub
from app.data import db, repo_published as repo
from app.jobs import car_price_job as job

TODAY = "1405-08-03"
ROW = (
    '<tr><td>{n}</td><td>1404</td><td><span class="price-range">{p}</span></td>'
    '<td>-</td><td>-</td><td><span class="trend-up">\u25b2 1.1</span></td></tr>'
)


def _html() -> str:
    rows = [("A", "1,000,000,000"), ("B", "50,000,000,000"),
            ("C", "200,000,000,000"), ("D", "\u2014")]
    return "<table>" + "".join(ROW.format(n=n, p=p) for n, p in rows) + "</table>"


def _conn(tmp_path):
    path = tmp_path / "t.db"
    db.migrate(path, tmp_path)
    return db.connect(path)


def test_auto_rows_keeps_luxury_drops_extreme_and_empty():
    names = [r["name"] for r in pub.auto_rows(_html())]
    assert names == ["A", "B"]


def test_stamp_and_day():
    moment = datetime(2026, 10, 25, 21, 0, tzinfo=timezone.utc)
    assert pub.stamp_and_day(moment) == ("2026-10-25 21:00:00", "2026-10-26")


def test_photo_of_today_blocks_auto(tmp_path):
    conn = _conn(tmp_path)
    repo.replace(conn, "2026-10-25", [{"n": 1}])
    assert not repo.replace_auto(conn, "2026-10-25", [{"n": 2}], "2026-10-25 10:00:00")
    assert repo.get(conn)["rows"] == [{"n": 1}]


def test_old_photo_lets_auto_in(tmp_path):
    conn = _conn(tmp_path)
    repo.replace(conn, "2026-10-24", [{"n": 1}])
    assert repo.replace_auto(conn, "2026-10-25", [{"n": 2}], "2026-10-25 10:00:00")
    assert repo.get_source(conn) == "auto"


def test_photo_replaces_auto(tmp_path):
    conn = _conn(tmp_path)
    repo.replace_auto(conn, "2026-10-25", [{"n": 2}], "2026-10-25 10:00:00")
    repo.replace(conn, "2026-10-25", [{"n": 3}])
    assert repo.get_source(conn) == "photo"


def test_older_auto_does_not_overwrite_newer(tmp_path):
    conn = _conn(tmp_path)
    repo.replace_auto(conn, "2026-10-25", [{"n": 2}], "2026-10-25 11:00:00")
    assert not repo.replace_auto(conn, "2026-10-25", [{"n": 1}], "2026-10-25 10:00:00")


def test_run_once_calls_on_fresh(monkeypatch):
    async def fake():
        return f'"dateModified": "{TODAY}"'
    monkeypatch.setattr(f, "fetch_page", fake)
    monkeypatch.setattr(f, "save_raw", lambda h: None)
    got = []
    assert asyncio.run(job.run_once(TODAY, got.append)) == "fresh"
    assert len(got) == 1
