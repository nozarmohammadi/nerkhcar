"""Tests for the 1car.ir raw page helpers (no network)."""
import os

from app.adapters import car_price_fetch as f


def _page(day: str) -> str:
    return f'"dateModified": "{day}" price-range ' + "x" * f.MIN_BYTES


def test_looks_valid():
    assert f.looks_valid(_page("1405-08-03"))
    assert not f.looks_valid("<html>error</html>")


def test_save_raw_names_file_by_page_date(tmp_path):
    path = f.save_raw(_page("1405-08-03"), tmp_path)
    assert path.name == "price-1405-08-03.html"
    assert path.exists()
    assert not list(tmp_path.glob("*.tmp"))


def test_prune_keeps_newest(tmp_path):
    for i in range(5):
        p = tmp_path / f"price-{i}.html"
        p.write_text("x")
        os.utime(p, (1000 + i, 1000 + i))
    f.prune(tmp_path, keep=2)
    names = sorted(x.name for x in tmp_path.glob("price-*.html"))
    assert names == ["price-3.html", "price-4.html"]
