"""Tests for manual backup pruning in tools/backup_db.py."""
import importlib.util
import os
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "backup_db", Path(__file__).resolve().parent.parent / "tools" / "backup_db.py"
)
mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(mod)

NOW = 2_000_000_000
DAY = 86400


def _make(folder, name, age_days):
    p = folder / name
    p.write_bytes(b"x")
    t = NOW - age_days * DAY
    os.utime(p, (t, t))
    return p


def test_old_extra_files_removed_daily_untouched(tmp_path):
    for i in range(5):
        _make(tmp_path, f"nerkhcar.pre-new{i}.db", 1)
    for i in range(7):
        _make(tmp_path, f"nerkhcar.pre-old{i}.db", 30 + i)
    daily = _make(tmp_path, "daily.20260101-033000.db", 90)
    removed = mod.prune_manual(tmp_path, now=NOW)
    assert len(removed) == 2
    assert daily.exists()


def test_few_old_files_all_kept(tmp_path):
    for i in range(5):
        _make(tmp_path, f"nerkhcar.pre-old{i}.db", 60)
    assert mod.prune_manual(tmp_path, now=NOW) == []


def test_many_recent_files_all_kept(tmp_path):
    for i in range(12):
        _make(tmp_path, f"nerkhcar.pre-new{i}.db", 2)
    assert mod.prune_manual(tmp_path, now=NOW) == []
