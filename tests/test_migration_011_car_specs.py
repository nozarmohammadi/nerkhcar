"""Migration 011 creates car_specs keyed by trim_id."""
import sqlite3

import pytest

from app.data import db


def _migrated(path):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    for f in sorted(db.MIGRATIONS_DIR.glob("*.sql")):
        conn.executescript(f.read_text(encoding="utf-8"))
    return conn


def _trim(conn):
    conn.execute("INSERT INTO brands(name) VALUES ('b')")
    conn.execute("INSERT INTO models(brand_id, name) VALUES (1, 'm')")
    conn.execute("INSERT INTO trims(model_id, name) VALUES (1, 't')")
    conn.commit()


def test_car_specs_table_and_unique_trim(tmp_path):
    conn = _migrated(tmp_path / "t.db")
    _trim(conn)
    sql = (
        "INSERT INTO car_specs(trim_id, source, source_slug, source_url,"
        " specs_json) VALUES (1, 'zoomit', 's', 'u', '{}')"
    )
    conn.execute(sql)
    row = conn.execute("SELECT reviewed FROM car_specs").fetchone()
    assert row[0] == 0
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql)


def test_car_specs_rejects_unknown_trim(tmp_path):
    conn = _migrated(tmp_path / "t.db")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO car_specs(trim_id, source, source_slug, source_url,"
            " specs_json) VALUES (999, 'zoomit', 's', 'u', '{}')"
        )
