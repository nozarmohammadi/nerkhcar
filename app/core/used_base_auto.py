"""Build a fallback used-car base price from the daily table (pure logic)."""
from datetime import datetime

from app.core import jalali
from app.core.used_estimate import Base, interp

# (age in years, price factor); a guess to be calibrated later.
AGE_CURVE = [
    (0, 1.00), (1, 0.88), (2, 0.78), (3, 0.73),
    (5, 0.65), (8, 0.57), (12, 0.48),
]
FALLBACK_SAMPLES = 3


def current_year(now: datetime) -> int:
    """Current Jalali year, taken from the date."""
    return jalali.to_jalali(now.year, now.month, now.day)[0]


def age_factor(age: int) -> float:
    """Price factor for a car of this age; never below the last point."""
    return interp(max(age, 0), AGE_CURVE)


def base_from_daily(
    daily_price_m: float, car_year: int, published_at: datetime,
    now: datetime,
) -> Base:
    """Base = daily price x age factor, marked as a fallback."""
    age = current_year(now) - car_year
    return Base(
        price=daily_price_m * age_factor(age),
        samples=FALLBACK_SAMPLES,
        updated_at=published_at,
        is_fallback=True,
    )
