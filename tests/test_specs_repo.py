"""Tests for repo_specs: only reviewed rows are visible."""
import json
import sqlite3

from app.data import repo_specs


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        "CREATE TABLE models(id INTEGER PRIMARY KEY, name TEXT);"
        "CREATE TABLE trims(id INTEGER PRIMARY KEY, model_id INTEGER);"
        "CREATE TABLE car_specs(trim_id INTEGER PRIMARY KEY, "
        "source_slug TEXT, specs_json TEXT, reviewed INTEGER);"
        "INSERT INTO models VALUES (1,'m1'),(2,'m2');"
        "INSERT INTO trims VALUES (10,1),(20,2);"
    )
    conn.execute(
        "INSERT INTO car_specs VALUES (10,'saipa-111',?,1)",
        (json.dumps({"seats": "5"}),))
    conn.execute(
        "INSERT INTO car_specs VALUES (20,'ikco-dena',?,0)",
        (json.dumps({"seats": "5"}),))
    return conn


def test_list_only_reviewed():
    rows = repo_specs.list_reviewed(_db())
    assert [r["trim_id"] for r in rows] == [10]
    assert rows[0]["slug"] == "saipa-111"


def test_get_reviewed_and_unreviewed():
    conn = _db()
    got = repo_specs.get(conn, 10)
    assert got == {"name": "m1", "slug": "saipa-111", "specs": {"seats": "5"}}
    assert repo_specs.get(conn, 20) is None
    assert repo_specs.get(conn, 999) is None
