"""Test: every logged estimate carries the model version (A10)."""
from app.core.model_version import MODEL_VERSION
from app.data import db, repo_estimates


def test_estimate_log_stores_model_version(tmp_path):
    db_path = tmp_path / "t.db"
    backups = tmp_path / "bk"
    backups.mkdir()
    db.migrate(db_path, backups)
    conn = db.connect(db_path)
    result = {"fair": (900, 1000), "quick_sale": (800, 900), "listing": (1000, 1100)}
    repo_estimates.add(conn, 5, {"name": "A"}, result)
    row = conn.execute("SELECT model_version, low, high FROM estimates_log").fetchone()
    conn.close()
    assert row[0] == MODEL_VERSION
    assert (row[1], row[2]) == (900, 1000)
