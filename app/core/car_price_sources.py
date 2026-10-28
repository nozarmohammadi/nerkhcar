"""Per-source daily state and the 1car + hamrah-mechanic row logic (pure)."""
from app.core import car_price_publish as pub, my_car_input

ONECAR = "1car"
HM = "hm"


def new_state() -> dict:
    """Loop state: alert counters plus the per-day source state."""
    return {"fails": 0, "sent": set(), "day": None, "done": set(),
            "slots": set(), "hm_rows": [], "pub": None}


def roll(state: dict, day: str) -> None:
    """Start a clean day when the date changed; nothing old is carried over."""
    if state["day"] != day:
        state.update(day=day, done=set(), slots=set(), hm_rows=[], pub=None)


def names(html: str | None) -> list[str]:
    """Names of today's 1car rows; empty when the page is missing."""
    return [r["name"] for r in pub.auto_rows(html)] if html else []


def extra_rows(ours: list[str], hm_rows: list[dict]) -> list[dict]:
    """hamrah-mechanic rows whose model 1car lacks (same rule as missing_slugs)."""
    own = [my_car_input.norm(n) for n in ours]
    return [r for r in hm_rows
            if not any(my_car_input.norm(r["name"]) in o for o in own)]


def plan(state: dict, final: bool) -> str | None:
    """What to publish now: 'full', 'onecar', 'hm' (fallback after final) or None."""
    done = state["done"]
    if ONECAR in done:
        return "full" if HM in done else "onecar"
    return "hm" if HM in done and final else None
