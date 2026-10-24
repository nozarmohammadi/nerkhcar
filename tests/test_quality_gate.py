from app.core import quality_gate as g


def _run(ours, a, b, yesterday=None):
    refs = [("a", a, a), ("b", b, b)]
    return g.evaluate((ours, ours), refs, yesterday)


def test_green_close():
    r = _run(100, 100, 102)
    assert (r.confidence, r.status, r.widen, r.reasons) == (
        "green", "published", False, ())


def test_five_percent_is_green():
    assert _run(105, 100, 100).confidence == "green"


def test_yellow_published_and_widen():
    r = _run(107, 100, 100)
    assert (r.confidence, r.status, r.widen) == ("yellow", "published", True)
    assert r.diff_pct == 7.0


def test_ten_percent_is_orange_held():
    r = _run(110, 100, 100)
    assert (r.confidence, r.status, r.widen) == ("orange", "held", False)


def test_fifteen_percent_is_orange():
    assert _run(115, 100, 100).confidence == "orange"


def test_sixteen_percent_is_red_blocked():
    r = _run(116, 100, 100)
    assert (r.confidence, r.status) == ("red", "blocked")


def test_worst_reference_decides():
    r = _run(100, 100, 130)
    assert (r.confidence, r.status) == ("red", "blocked")


def test_agreeing_refs_far_from_us_are_held():
    r = _run(112, 100, 101)
    assert (r.confidence, r.status) == ("orange", "held")


def test_one_reference_is_no_data():
    r = g.evaluate((100, 100), [("a", 100, 100)])
    assert (r.confidence, r.status, r.reasons) == ("red", "held", ("no_data",))
    assert r.diff_pct is None


def test_same_source_twice_is_no_data():
    refs = [("a", 100, 100), ("a", 101, 101)]
    assert g.evaluate((100, 100), refs).reasons == ("no_data",)


def test_invalid_reference_is_ignored():
    refs = [("a", 100, 100), ("b", 0, 0), ("c", 100, 100)]
    assert g.evaluate((100, 100), refs).confidence == "green"
    assert g.evaluate((100, 100), refs[:2]).reasons == ("no_data",)


def test_jump_holds_even_when_green():
    r = _run(100, 100, 100, (80, 80))
    assert (r.confidence, r.status) == ("green", "held")
    assert "jump" in r.reasons


def test_exactly_ten_percent_is_not_a_jump():
    r = _run(110, 110, 110, (100, 100))
    assert r.status == "published"


def test_jump_keeps_blocked():
    r = _run(120, 100, 100, (80, 80))
    assert r.status == "blocked"


def test_range_uses_midpoint():
    refs = [("a", 100, 100), ("b", 100, 100)]
    r = g.evaluate((95, 105), refs)
    assert (r.confidence, r.diff_pct) == ("green", 0.0)
