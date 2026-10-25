import sqlite3

import pytest

from app.data import db, repo_used_base


def _conn(tmp_path):
    db.migrate(tmp_path / "t.db", tmp_path)
    conn = db.connect(tmp_path / "t.db")
    conn.execute("INSERT INTO brands(name) VALUES ('b')")
    conn.execute("INSERT INTO models(brand_id, name) VALUES (1, 'm')")
    conn.execute("INSERT INTO trims(model_id, name) VALUES (1, 't')")
    conn.commit()
    return conn


def test_get_missing_returns_none(tmp_path):
    assert repo_used_base.get(_conn(tmp_path), 1, 1400) is None


def test_upsert_and_get(tmp_path):
    conn = _conn(tmp_path)
    repo_used_base.upsert(conn, 1, 1400, 1000, 3, "A", 5)
    got = repo_used_base.get(conn, 1, 1400)
    assert (got["price"], got["samples"], got["liquidity"]) == (1000, 3, "A")


def test_upsert_twice_keeps_one_row(tmp_path):
    conn = _conn(tmp_path)
    repo_used_base.upsert(conn, 1, 1400, 1000, 3, "A", 5)
    repo_used_base.upsert(conn, 1, 1400, 1100, 4, "B", 5)
    count = conn.execute("SELECT COUNT(*) FROM used_base").fetchone()[0]
    assert count == 1
    assert repo_used_base.get(conn, 1, 1400)["price"] == 1100


def test_bad_liquidity_rejected(tmp_path):
    conn = _conn(tmp_path)
    with pytest.raises(sqlite3.IntegrityError):
        repo_used_base.upsert(conn, 1, 1400, 1000, 3, "Z", 5)
