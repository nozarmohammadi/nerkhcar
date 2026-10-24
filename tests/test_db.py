"""تست لایهٔ دیتابیس."""
from app.data import db, repo_admins, repo_audit, repo_catalog, repo_prices


def test_migrate_is_idempotent(tmp_path):
    path = tmp_path / "t.db"
    assert db.migrate(path, tmp_path) == ["001_init", "002_ai_usage"]
    assert db.migrate(path, tmp_path) == []


def test_price_upsert_keeps_history(conn):
    brand = repo_catalog.add_brand(conn, "b")
    model = repo_catalog.add_model(conn, brand, "m")
    conn.execute("INSERT INTO trims(model_id, name) VALUES (?, 't')", (model,))
    repo_prices.upsert_price(conn, 1, 1403, 100, 110, "green", "published", 1)
    repo_prices.upsert_price(conn, 1, 1403, 105, 115, "green", "published", 1)
    price = repo_prices.get_price(conn, 1, 1403)
    assert (price.low, price.high) == (105, 115)
    count = conn.execute("SELECT count(*) FROM price_history").fetchone()[0]
    assert count == 2


def test_admin_roundtrip(conn):
    repo_admins.add_admin(conn, 42, "owner")
    assert repo_admins.get_admin(conn, 42).role == "owner"
    assert repo_admins.get_admin(conn, 99) is None


def test_audit_log(conn):
    repo_audit.add_entry(conn, 1, "login")
    assert repo_audit.recent(conn)[0]["action"] == "login"
