"""Tests for the per-part body damage drop."""
from datetime import datetime, timezone

import pytest

from app.core import body_parts as bp
from app.core.used_config import CFG
from app.core.used_estimate import Base, Car, body_factor, estimate


def test_clean_and_unknown():
    assert bp.classify("repaint", []) == "clean"
    assert bp.classify("unknown", ["hood"]) == "unknown"


def test_single_replaced_door_is_five_percent():
    assert bp.classify("replaced", ["front_left_door"]) == "drop_5"


def test_repaint_parts_are_summed():
    assert bp.classify("repaint", ["hood", "front_fender"]) == "drop_7"


def test_drop_is_capped():
    assert bp.classify("replaced", list(bp.REPAINT_DROP)) == "drop_35"


def test_body_factor_codes():
    assert body_factor("drop_5", CFG) == pytest.approx(0.95)
    assert body_factor("clean", CFG) == 1.0
    assert body_factor("drop_x", CFG) is None
    assert body_factor("bad", CFG) is None


def test_engine_uses_drop_code():
    now = datetime.now(timezone.utc)
    base = Base(price=1000.0, samples=5, updated_at=now)
    ok = estimate(Car(1403, None, "drop_5", "healthy"), base, None, now)
    assert ok["status"] == "ok"
    assert ok["central"] == pytest.approx(950.0)
    bad = estimate(Car(1403, None, "drop_x", "healthy"), base, None, now)
    assert bad["status"] == "invalid"
