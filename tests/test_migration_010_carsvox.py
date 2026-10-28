"""Migration 010 removes only the test brand carsvox."""
import sqlite3

from app.data import db

SQL = "010_remove_test_carsvox.sql"


def _upto_009(path):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    for f in sorted(db.MIGRATIONS_DIR.glob("*.sql")):
        if f.stem < "010":
            conn.executescript(f.read_text(encoding="utf-8"))
    return conn


def _seed(conn):
    for brand in ("carsvox", "keep"):
        conn.execute("INSERT INTO brands(name) VALUES (?)", (brand,))
        bid = conn.execute(
            "SELECT id FROM brands WHERE name=?", (brand,)
        ).fetchone()[0]
        conn.execute("INSERT INTO models(brand_id, name) VALUES (?, 'm')", (bid,))
        mid = conn.execute(
            "SELECT id FROM models WHERE brand_id=?", (bid,)
        ).fetchone()[0]
        conn.execute("INSERT INTO trims(model_id, name) VALUES (?, 't')", (mid,))
        tid = conn.execute(
            "SELECT id FROM trims WHERE model_id=?", (mid,)
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO reference_prices(trim_id, year, source_name, low, high)"
            " VALUES (?, 1400, 's', 1, 2)", (tid,))
    keep = conn.execute(
        "SELECT t.id FROM trims t JOIN models m ON m.id=t.model_id"
        " JOIN brands b ON b.id=m.brand_id WHERE b.name='keep'"
    ).fetchone()[0]
    conn.execute(
        "INSERT INTO prices(trim_id, year, low, high, confidence, status)"
        " VALUES (?, 1400, 1, 2, 'green', 'published')", (keep,))
    conn.commit()


def _count(conn, table):
    return conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]


def test_removes_only_carsvox(tmp_path):
    conn = _upto_009(tmp_path / "t.db")
    _seed(conn)
    sql = (db.MIGRATIONS_DIR / SQL).read_text(encoding="utf-8")
    conn.executescript(sql)
    assert _count(conn, "brands") == 1
    for table in ("models", "trims", "reference_prices", "prices"):
        assert _count(conn, table) == 1
    conn.executescript(sql)
    assert _count(conn, "brands") == 1
