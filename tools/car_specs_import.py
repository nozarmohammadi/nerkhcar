"""Import fetched Zoomit specs into car_specs.

Dry run by default (works on a copy of the db). --apply writes the live db
after db.migrate() has made its own backup.
Usage: PYTHONPATH=. venv/bin/python tools/car_specs_import.py SPECS.json [--apply]
"""
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

from app.data import db
from tools import zoomit_slug_map as zm

DB_PATH = Path("data/nerkhcar.db")
URL = "https://www.zoomit.ir/product/"
SQL = (
    "INSERT OR IGNORE INTO car_specs(trim_id, source, source_slug, source_url,"
    " specs_json, reviewed) VALUES (?, ?, ?, ?, ?, ?)"
)


def build_rows(specs_by_slug):
    rows = []
    for match, mapping in (("exact", zm.exact()), ("family", zm.family())):
        for trim_id, slug in sorted(mapping.items()):
            specs = specs_by_slug.get(slug)
            if not specs:
                continue
            payload = json.dumps(dict(specs, _match=match), ensure_ascii=False)
            reviewed = 1 if match == "exact" else 0
            rows.append((trim_id, "zoomit", slug, URL + slug + "/", payload, reviewed))
    return rows


def write_rows(conn, rows):
    before = conn.total_changes
    conn.executemany(SQL, rows)
    conn.commit()
    return conn.total_changes - before


def prepare(apply):
    if apply:
        return DB_PATH, Path("backups")
    tmp = Path(tempfile.mkdtemp())
    src = sqlite3.connect("file:" + str(DB_PATH) + "?mode=ro", uri=True)
    dst = sqlite3.connect(tmp / "copy.db")
    src.backup(dst)
    src.close()
    dst.close()
    return tmp / "copy.db", tmp


def sample(conn):
    sql = (
        "SELECT t.id, m.name, s.source_slug, s.reviewed,"
        " json_extract(s.specs_json, '$.displacement'),"
        " json_extract(s.specs_json, '$.power')"
        " FROM car_specs s JOIN trims t ON t.id = s.trim_id"
        " JOIN models m ON m.id = t.model_id ORDER BY random() LIMIT 10"
    )
    for row in conn.execute(sql):
        print(row)


def main(specs_path, apply):
    specs = json.load(open(specs_path, encoding="utf-8"))
    rows = build_rows(specs)
    target, backups = prepare(apply)
    done = db.migrate(target, backups)
    conn = sqlite3.connect(target)
    conn.execute("PRAGMA foreign_keys=ON")
    added = write_rows(conn, rows)
    total = conn.execute("SELECT count(*) FROM car_specs").fetchone()[0]
    exact = sum(1 for r in rows if r[5] == 1)
    print("apply" if apply else "dry-run", "migrations", done)
    print("rows", len(rows), "exact", exact, "family", len(rows) - exact)
    print("added", added, "total in table", total)
    sample(conn)
    conn.close()


if __name__ == "__main__":
    main(sys.argv[1], "--apply" in sys.argv[2:])
