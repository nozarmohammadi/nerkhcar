"""Tests for the read-only API layer."""
import asyncio
import json
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
from aiohttp.test_utils import TestClient, TestServer

from app.api.db_ro import connect_ro
from app.api.server import build_app

FMT = "%Y-%m-%d %H:%M:%S"
ROWS = [{"name": "x", "year": 1404, "price_m": 100}]


def _db(tmp_path, published_at=None, with_table=True):
    path = tmp_path / "t.db"
    conn = sqlite3.connect(path)
    if with_table:
        conn.execute(
            "CREATE TABLE published_daily (id INTEGER PRIMARY KEY, day TEXT, "
            "rows_json TEXT, published_at TEXT, source TEXT)"
        )
        if published_at is not None:
            conn.execute(
                "INSERT INTO published_daily VALUES (1, 'd', ?, ?, 'auto')",
                (json.dumps(ROWS), published_at),
            )
    else:
        conn.execute("CREATE TABLE other (a INTEGER)")
    conn.commit()
    conn.close()
    return path


def _get(path, url):
    async def run():
        async with TestClient(TestServer(build_app(path))) as client:
            resp = await client.get(url)
            return resp.status, await resp.json()

    return asyncio.run(run())


def _ago(hours):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(FMT)


def test_health(tmp_path):
    status, body = _get(_db(tmp_path), "/api/health")
    assert status == 200 and body == {"ok": True}


def test_empty_table(tmp_path):
    status, body = _get(_db(tmp_path), "/api/prices/daily")
    assert status == 200
    assert body == {"status": "empty", "rows": []}


def test_fresh_prices_returned(tmp_path):
    status, body = _get(_db(tmp_path, _ago(2)), "/api/prices/daily")
    assert status == 200
    assert body["status"] == "ok" and body["rows"] == ROWS


def test_stale_prices_hidden(tmp_path):
    status, body = _get(_db(tmp_path, _ago(100)), "/api/prices/daily")
    assert status == 200
    assert body["status"] == "stale" and body["rows"] == []


def test_db_problem_gives_503(tmp_path):
    status, body = _get(_db(tmp_path, with_table=False), "/api/prices/daily")
    assert status == 503 and body["status"] == "error"


def test_connection_is_read_only(tmp_path):
    conn = connect_ro(_db(tmp_path, _ago(1)))
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM published_daily")
    conn.close()
