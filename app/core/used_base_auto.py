"""Build a fallback used-car base price from the daily table (pure logic)."""
from datetime import datetime

from app.core import jalali
from app.core.used_estimate import Base, interp

# (age in years, price factor); a guess to be calibrated later.
AGE_CURVE = [
    (0, 1.00), (1, 0.88), (2, 0.78), (3, 0.73),
    (5, 0.65), (8, 0.57), (12, 0.48),
    (16, 0.38), (20, 0.32),
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


def base_exact(price_m: float, published_at: datetime) -> Base:
    """Table price of the exact model year, used as is (not a fallback)."""
    return Base(price=price_m, samples=FALLBACK_SAMPLES, updated_at=published_at)


def base_aged(
    newest_m: float, newest_year: int, car_year: int,
    published_at: datetime, now: datetime,
) -> Base:
    """Newest table price scaled by the age ratio of the two years."""
    now_year = current_year(now)
    ratio = age_factor(now_year - car_year) / age_factor(now_year - newest_year)
    return Base(
        price=newest_m * min(ratio, 1.0), samples=FALLBACK_SAMPLES,
        updated_at=published_at, is_fallback=True,
    )
