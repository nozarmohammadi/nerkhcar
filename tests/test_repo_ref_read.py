from app.core import quality_gate
from app.data import db, repo_ref_read, repo_refs


def _setup(tmp_path):
    path = tmp_path / "t.db"
    db.migrate(path, tmp_path)
    conn = db.connect(path)
    conn.execute("INSERT INTO brands(name) VALUES ('b')")
    brand_id = conn.execute("SELECT id FROM brands").fetchone()["id"]
    model_id = repo_refs.ensure_model(conn, brand_id, "m")
    trim_id = repo_refs.ensure_trim(conn, model_id, "t")
    conn.commit()
    return conn, trim_id


def _add(conn, trim_id, year, source, price):
    repo_refs.add_reference(conn, trim_id, year, source, price, price, 1)
    conn.commit()


def test_empty_when_no_references(tmp_path):
    conn, trim_id = _setup(tmp_path)
    assert repo_ref_read.latest_per_source(conn, trim_id, 1404) == []


def test_newest_entry_of_each_source_wins(tmp_path):
    conn, trim_id = _setup(tmp_path)
    _add(conn, trim_id, 1404, "a", 100)
    _add(conn, trim_id, 1404, "a", 110)
    _add(conn, trim_id, 1404, "b", 105)
    got = repo_ref_read.latest_per_source(conn, trim_id, 1404)
    assert got == [("a", 110, 110), ("b", 105, 105)]


def test_other_year_is_excluded(tmp_path):
    conn, trim_id = _setup(tmp_path)
    _add(conn, trim_id, 1403, "a", 100)
    assert repo_ref_read.latest_per_source(conn, trim_id, 1404) == []


def test_result_feeds_the_gate(tmp_path):
    conn, trim_id = _setup(tmp_path)
    _add(conn, trim_id, 1404, "a", 100)
    _add(conn, trim_id, 1404, "b", 102)
    refs = repo_ref_read.latest_per_source(conn, trim_id, 1404)
    result = quality_gate.evaluate((101, 101), refs)
    assert (result.confidence, result.status) == ("green", "published")
