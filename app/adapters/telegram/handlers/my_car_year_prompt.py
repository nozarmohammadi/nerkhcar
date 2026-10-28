"""Choose the year question text by the calendar the table uses."""
from app.adapters.telegram import dbrun
from app.adapters.telegram.texts import my_car as t
from app.config import Settings
from app.core import my_car_years
from app.data import repo_published


def year_prompt(settings: Settings, name: str) -> str:
    """Gregorian example for imported cars, Jalali example otherwise."""
    published = dbrun.run(settings, repo_published.get)
    rows = published["rows"] if published else []
    last = my_car_years.last_year(rows, name)
    if last is not None and my_car_years.is_greg(last):
        return t.ASK_YEAR_GREG
    return t.ASK_YEAR_TYPED
