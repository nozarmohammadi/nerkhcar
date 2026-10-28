"""Map body-part selections to the estimate engine body code."""

# Price drop in percent for one repainted part (public market averages).
REPAINT_DROP = {
    "hood": 4, "front_left_door": 4, "front_right_door": 4,
    "rear_left_door": 4, "rear_right_door": 4, "trunk": 4,
    "front_fender": 3, "rear_fender": 3,
}
# Replacing a part costs about 1 percent more than repainting it.
REPLACED_EXTRA = 1
# Cap of the whole body drop, in percent.
MAX_DROP = 35


def drop_percent(mode: str | None, parts: list[str] | None) -> int:
    """Return the summed price drop in percent, capped at MAX_DROP."""
    extra = REPLACED_EXTRA if mode == "replaced" else 0
    total = sum(
        REPAINT_DROP[p] + extra
        for p in set(parts or []) if p in REPAINT_DROP
    )
    return min(total, MAX_DROP)


def classify(mode: str | None, parts: list[str] | None) -> str:
    """Return 'clean', 'unknown' or 'drop_N' for the estimate engine."""
    if mode == "unknown":
        return "unknown"
    if not set(parts or []):
        return "clean"
    if mode not in ("repaint", "replaced"):
        return "unknown"
    drop = drop_percent(mode, parts)
    return f"drop_{drop}" if drop else "clean"
