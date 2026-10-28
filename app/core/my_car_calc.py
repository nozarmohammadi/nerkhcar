"""Turn the form answers into an estimate (pure logic, no Telegram)."""
from datetime import datetime, timezone

from app.core import model_lookup, my_car_options as opt
from app.core import my_car_years, price_age, used_base_auto
from app.core.used_config import CFG
from app.core.used_estimate import Car, estimate

FMT = "%Y-%m-%d %H:%M:%S"
# Mileage is an unverified guess: keep the factor flat until calibrated.
FLAT_KM = [(0.5, 1.0), (3.0, 1.0)]


def _published(stamp: str) -> datetime:
    return datetime.strptime(stamp, FMT).replace(tzinfo=timezone.utc)


def _base(data: dict, answers: dict, found: tuple, price: float, now):
    """Exact table year as is; otherwise the newest year aged to the car year."""
    stamp = _published(data["published_at"])
    if found[1]:
        return used_base_auto.base_exact(price, stamp)
    year, newest = model_lookup.newest_price(data["rows"], answers["name"])
    return used_base_auto.base_aged(
        newest, my_car_years.to_jalali(year),
        my_car_years.to_jalali(answers["year"]), stamp, now)


def compute(data: dict, answers: dict, now: datetime | None = None, zero: float | None = None) -> dict:
    """data: published table {rows, published_at}; answers: model name,
    year and option indexes km, body, chassis. Returns the engine result;
    status is 'insufficient' when the table is missing or expired."""
    now = now or datetime.now(timezone.utc)
    if data is None or price_age.status(data["published_at"], now) == "expired":
        return {"status": "insufficient", "reason": "stale"}
    found = model_lookup.price_for(data["rows"], answers["name"], answers["year"])
    km = answers["km"]
    body_answer = answers["body"]
    chassis_answer = answers["chassis"]
    body = body_answer if isinstance(body_answer, str) else opt.body_of(body_answer)
    chassis = (
        chassis_answer
        if isinstance(chassis_answer, str)
        else opt.chassis_of(chassis_answer)
    )
    if found is None or body is None or chassis is None:
        return {"status": "insufficient", "reason": "samples"}
    base_price = zero if zero is not None else found[0]
    year_j = my_car_years.to_jalali(answers["year"])
    base = _base(data, answers, found, base_price, now)
    car = Car(year_j, km, body, chassis)
    cfg = {**CFG, "current_year": used_base_auto.current_year(now),
           "mileage_curve": FLAT_KM}
    return estimate(car, base, zero, now, cfg)
