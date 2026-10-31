"""Tests for the read-only FX endpoint (dollar, coin, gold from fx_cache)."""
import asyncio
import sqlite3
from datetime import datetime, timedelta, timezone

from aiohttp.test_utils import TestClient, TestServer

from app.api import fx
from app.api.server import build_app

FMT = "%Y-%m-%d %H:%M:%S"
SYMBOLS = {"price_dollar_rl": 271060, "sekee": 266785000, "geram18": 26223500}


def _db(tmp_path, age_hours=1, skip=()):
    """Create a temp db with fx_cache rows of a given age; return its path."""
    path = tmp_path / "fx.db"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE fx_cache (symbol TEXT PRIMARY KEY, value REAL NOT NULL, "
        "source TEXT NOT NULL, fetched_at TEXT NOT NULL)"
    )
    stamp = (datetime.now(timezone.utc) - timedelta(hours=age_hours)).strftime(FMT)
    for symbol, value in SYMBOLS.items():
        if symbol not in skip:
            conn.execute("INSERT INTO fx_cache VALUES (?, ?, 'web', ?)", (symbol, value, stamp))
    conn.commit()
    conn.close()
    return path


def _latest(path):
    conn = sqlite3.connect(path)
    try:
        return fx.latest(conn)
    finally:
        conn.close()


def test_rows_in_fixed_order_with_age(tmp_path):
    data = _latest(_db(tmp_path, age_hours=2))
    assert data["status"] == "ok"
    assert [r["key"] for r in data["rows"]] == ["dollar", "coin", "gold"]
    assert data["rows"][0]["toman"] == 271060
    assert 118 <= data["rows"][0]["age_min"] <= 122


def test_missing_symbol_is_skipped(tmp_path):
    data = _latest(_db(tmp_path, skip=("sekee",)))
    assert [r["key"] for r in data["rows"]] == ["dollar", "gold"]


def test_older_than_72_hours_is_hidden(tmp_path):
    data = _latest(_db(tmp_path, age_hours=80))
    assert data == {"status": "empty", "rows": []}


def test_endpoint_returns_rows(tmp_path):
    path = _db(tmp_path)

    async def go():
        async with TestClient(TestServer(build_app(path))) as client:
            resp = await client.get("/api/fx")
            return resp.status, await resp.json()

    status, body = asyncio.run(go())
    assert status == 200 and body["status"] == "ok" and len(body["rows"]) == 3
