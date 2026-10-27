"""برند و مدل خودرو."""
import sqlite3


def add_brand(conn: sqlite3.Connection, name: str) -> int:
    cur = conn.execute("INSERT INTO brands(name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def list_brands(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT id, name FROM brands ORDER BY name").fetchall()
    return [dict(r) for r in rows]


def add_model(conn: sqlite3.Connection, brand_id: int, name: str) -> int:
    cur = conn.execute(
        "INSERT INTO models(brand_id, name) VALUES (?,?)", (brand_id, name)
    )
    conn.commit()
    return cur.lastrowid


def list_models(conn: sqlite3.Connection, brand_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT id, name FROM models WHERE brand_id=? ORDER BY name", (brand_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def get_brand(conn: sqlite3.Connection, brand_id: int) -> dict | None:
    row = conn.execute(
        "SELECT id, name FROM brands WHERE id=?", (brand_id,)
    ).fetchone()
    return dict(row) if row else None


def get_model(conn: sqlite3.Connection, model_id: int) -> dict | None:
    row = conn.execute(
        "SELECT id, brand_id, name FROM models WHERE id=?", (model_id,)
    ).fetchone()
    return dict(row) if row else None


def add_trim(conn: sqlite3.Connection, model_id: int, name: str) -> int:
    cur = conn.execute(
        "INSERT INTO trims(model_id, name) VALUES (?,?)", (model_id, name)
    )
    conn.commit()
    return cur.lastrowid


def list_trims(conn: sqlite3.Connection, model_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT id, name FROM trims WHERE model_id=? ORDER BY name", (model_id,)
    ).fetchall()
    return [dict(r) for r in rows]

def list_user_trims(conn: sqlite3.Connection) -> list[dict]:
    """Return trims with their brand and model names for user selection."""
    rows = conn.execute(
        "SELECT t.id AS trim_id, t.name AS trim, "
        "m.id AS model_id, m.name AS model, "
        "b.id AS brand_id, b.name AS brand "
        "FROM trims t "
        "JOIN models m ON m.id=t.model_id "
        "JOIN brands b ON b.id=m.brand_id "
        "ORDER BY m.name, t.name"
    ).fetchall()
    return [dict(r) for r in rows]
