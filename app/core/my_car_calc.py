"""Turn the form answers into an estimate (pure logic, no Telegram)."""
from datetime import datetime, timezone

from app.core import model_lookup, my_car_options as opt
from app.core import price_age, used_base_auto
from app.core.used_estimate import Car, estimate

FMT = "%Y-%m-%d %H:%M:%S"


def _published(stamp: str) -> datetime:
    return datetime.strptime(stamp, FMT).replace(tzinfo=timezone.utc)


def compute(data: dict, answers: dict, now: datetime | None = None) -> dict:
    """data: published table {rows, published_at}; answers: model name,
    year and option indexes km, body, chassis. Returns the engine result;
    status is 'insufficient' when the table is missing or expired."""
    now = now or datetime.now(timezone.utc)
    if data is None or price_age.status(data["published_at"], now) == "expired":
        return {"status": "insufficient", "reason": "stale"}
    found = model_lookup.price_for(data["rows"], answers["name"], answers["year"])
    km = opt.km_of(answers["km"])
    body, chassis = opt.body_of(answers["body"]), opt.chassis_of(answers["chassis"])
    if found is None or km is None or body is None or chassis is None:
        return {"status": "insufficient", "reason": "samples"}
    base = used_base_auto.base_from_daily(
        found[0], answers["year"], _published(data["published_at"]), now)
    car = Car(answers["year"], km, body, chassis)
    return estimate(car, base, None, now)
