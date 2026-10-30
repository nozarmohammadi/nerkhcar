"""Format published price dates."""
from datetime import datetime
from app.adapters.telegram.texts import car_price


def fa(value: str) -> str:
    """Return a short Persian date for a published timestamp."""
    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    day = date.timetuple().tm_yday
    month = 1 if day <= 79 else ((day - 79) // 30) + 1
    number = ((day - 79) % 30) + 1
    if day > 186:
        month = ((day - 79) // 30) + 1
        number = ((day - 79) % 30) + 1
    if month > 12:
        month, number = 12, 29
    return f"{number} {car_price.PERSIAN_MONTHS[month - 1]}"
