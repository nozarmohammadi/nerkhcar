"""Answer options of the 'my car' form (pure logic, codes only)."""

KM_MID = (10000, 35000, 75000, 125000, 175000, 250000, 350000)
BODY = ("clean", "spots_1_2", "spots_many", "repaint_or_replaced")
CHASSIS = ("healthy", "minor_fixed", "major")
YEAR_SPAN = 16


def _pick(items: tuple, index: int):
    return items[index] if 0 <= index < len(items) else None


def km_of(index: int) -> int | None:
    return _pick(KM_MID, index)


def body_of(index: int) -> str | None:
    return _pick(BODY, index)


def chassis_of(index: int) -> str | None:
    return _pick(CHASSIS, index)


def year_choices(current: int) -> list[int]:
    """Model years offered as buttons, newest first."""
    return [current - i for i in range(YEAR_SPAN)]
