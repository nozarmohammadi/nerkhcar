"""Same first word sits together, sub-models stay together inside it."""
from app.core import brand_groups as bg


def _row(name):
    return {"name": name, "year": 1405, "brand": "b"}


def test_same_first_word_together():
    rows = [_row("s LX"), _row("p 207 a"), _row("s soren"),
            _row("p 405"), _row("s SE"), _row("p 207 b")]
    names = [r["name"] for r in bg.grouped(rows)[0][1]]
    assert names == ["s LX", "s soren", "s SE", "p 207 a", "p 207 b", "p 405"]
