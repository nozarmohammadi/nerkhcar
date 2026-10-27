"""Used-car price estimate engine (pure logic, no Telegram)."""
from dataclasses import dataclass
from datetime import datetime

from app.core.used_config import CFG


@dataclass
class Car:
    year: int
    km: int
    body: str
    chassis: str
    color: str | None = None


@dataclass
class Base:
    price: float
    samples: int
    updated_at: datetime
    liquidity: str = "B"
    is_fallback: bool = False


def interp(x: float, curve: list) -> float:
    """Linear interpolation over (x, y) points, clamped at both ends."""
    if x <= curve[0][0]:
        return curve[0][1]
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return curve[-1][1]


def _invalid(car: Car, cfg: dict) -> bool:
    if car.km is not None and (car.km < 0 or car.km > cfg["limits"]["max_km"]):
        return True
    if car.year > cfg["current_year"]:
        return True
    if car.body not in cfg["body"] or car.chassis not in cfg["chassis"]:
        return True
    return car.color is not None and car.color not in cfg["color"]


def _km_factor(car: Car, cfg: dict) -> float:
    if car.km is None:
        return 1.0
    age = cfg["current_year"] - car.year
    expected = max(age * cfg["std_km_per_year"], cfg["min_expected_km"])
    return interp(car.km / expected, cfg["mileage_curve"])


def _damage_factor(car: Car, cfg: dict) -> float:
    body, chassis = cfg["body"][car.body], cfg["chassis"][car.chassis]
    worst, other = min(body, chassis), max(body, chassis)
    return worst * (1 - cfg["second_damage_weight"] * (1 - other))


def _spread(car: Car, base: Base, hours: float, warn: bool, cfg: dict) -> float:
    unknown = (car.body == "unknown") + (car.chassis == "unknown")
    s = cfg["spread"]["base"] + cfg["spread"]["unknown_answer_add"] * unknown
    if hours > cfg["freshness"]["fresh_hours"]:
        s *= cfg["freshness"]["stale_spread_mult"]
    if base.liquidity == "C":
        s *= cfg["spread"]["illiquid_mult"]
    if base.is_fallback:
        s *= cfg["zero_ref"]["fallback_spread_mult"]
    if warn:
        s *= cfg["zero_ref"]["warn_spread_mult"]
    return s


def estimate(car: Car, base: Base | None, zero: float | None,
             now: datetime, cfg: dict = CFG) -> dict:
    """Return status and, when ok, the three price bands (million toman)."""
    if _invalid(car, cfg):
        return {"status": "invalid"}
    if base is None or base.samples < cfg["min_samples_per_base"]:
        return {"status": "insufficient", "reason": "samples"}
    hours = (now - base.updated_at).total_seconds() / 3600
    if hours > cfg["freshness"]["max_hours"]:
        return {"status": "insufficient", "reason": "stale"}
    color = cfg["color"][car.color] if car.color else 1.0
    factor = _km_factor(car, cfg) * _damage_factor(car, cfg) * color
    factor = min(max(factor, cfg["total_floor"]), cfg["total_cap"])
    central = base.price * factor
    age = cfg["current_year"] - car.year
    warn = (zero is not None and age <= cfg["zero_ref"]["warn_max_age"]
            and central > zero)
    s = _spread(car, base, hours, warn, cfg)
    return {
        "status": "ok", "central": central, "warn_above_zero": warn,
        "confidence_low": base.is_fallback,
        "quick_sale": (central * (1 - 1.5 * s), central * (1 - 0.5 * s)),
        "fair": (central * (1 - 0.5 * s), central * (1 + 0.5 * s)),
        "listing": (central * (1 + 0.5 * s), central * (1 + 1.5 * s)),
    }
