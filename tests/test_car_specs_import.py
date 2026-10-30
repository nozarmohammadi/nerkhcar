"""car_specs import: row building and idempotent writes."""
import sqlite3

from app.data import db
from tools import car_specs_import as ci

SPECS = {"lamari-eama": {"power": "1"}, "saipa-atlas": {"power": "2"}}


def _conn(path):
    conn = sqlite3.connect(path)
    for f in sorted(db.MIGRATIONS_DIR.glob("*.sql")):
        conn.executescript(f.read_text(encoding="utf-8"))
    conn.execute("INSERT INTO brands(id, name) VALUES (1, 'b')")
    conn.execute("INSERT INTO models(id, brand_id, name) VALUES (1, 1, 'm')")
    for tid in (10, 77):
        conn.execute(
            "INSERT INTO trims(id, model_id, name) VALUES (?, 1, ?)",
            (tid, "t" + str(tid)),
        )
    conn.commit()
    return conn


def test_build_rows_flags_and_skips_missing():
    rows = {r[0]: r for r in ci.build_rows(SPECS)}
    assert rows[77][5] == 1
    assert rows[10][5] == 0
    assert {r[2] for r in rows.values()} == {"lamari-eama", "saipa-atlas"}
    assert '"_match": "exact"' in rows[77][4]


def test_write_rows_is_idempotent(tmp_path):
    conn = _conn(tmp_path / "t.db")
    rows = [r for r in ci.build_rows(SPECS) if r[0] in (10, 77)]
    assert ci.write_rows(conn, rows) == 2
    assert ci.write_rows(conn, rows) == 0
