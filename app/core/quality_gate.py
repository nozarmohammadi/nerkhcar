"""Quality gate: compare our price range with the control references.

Pure logic: no database and no Telegram. The caller passes the data in.
"""
from dataclasses import dataclass

GREEN_MAX = 5.0    # diff <= 5% -> green
YELLOW_MAX = 10.0  # 5% < diff < 10% -> yellow
ORANGE_MAX = 15.0  # 10% <= diff <= 15% -> orange; above -> red
JUMP_MAX = 10.0    # change vs yesterday above this needs manual approval

STATUS = {
    "green": "published",
    "yellow": "published",
    "orange": "held",
    "red": "blocked",
}


@dataclass(frozen=True)
class GateResult:
    confidence: str
    status: str
    widen: bool
    reasons: tuple[str, ...]
    diff_pct: float | None


def _mid(low: int, high: int) -> float:
    return (low + high) / 2


def _diff_pct(ours: float, ref: float) -> float:
    return abs(ours - ref) * 100 / ref


def _level(diff: float) -> str:
    if diff <= GREEN_MAX:
        return "green"
    if diff < YELLOW_MAX:
        return "yellow"
    if diff <= ORANGE_MAX:
        return "orange"
    return "red"


def _ref_mids(refs: list[tuple[str, int, int]]) -> list[float]:
    """Midpoint per distinct source; invalid ranges are ignored."""
    by_source = {}
    for source, low, high in refs:
        if low > 0 and high >= low:
            by_source[source] = _mid(low, high)
    return list(by_source.values())


def _is_jump(our_mid: float, yesterday: tuple[int, int] | None) -> bool:
    if yesterday is None:
        return False
    old = _mid(*yesterday)
    return old > 0 and _diff_pct(our_mid, old) > JUMP_MAX


def evaluate(
    ours: tuple[int, int],
    refs: list[tuple[str, int, int]],
    yesterday: tuple[int, int] | None = None,
) -> GateResult:
    """ours and yesterday are (low, high); refs are (source, low, high)."""
    mids = _ref_mids(refs)
    if not (ours[0] > 0 and ours[1] >= ours[0]) or len(mids) < 2:
        return GateResult("red", "held", False, ("no_data",), None)
    our_mid = _mid(*ours)
    worst = max(_diff_pct(our_mid, m) for m in mids)
    level = _level(worst)
    status = STATUS[level]
    reasons = [] if level == "green" else ["diff"]
    if status != "blocked" and _is_jump(our_mid, yesterday):
        status = "held"
        reasons.append("jump")
    return GateResult(
        level, status, level == "yellow", tuple(reasons), round(worst, 2))
