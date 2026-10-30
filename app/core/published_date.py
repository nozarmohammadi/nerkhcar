"""Format published timestamps as Persian dates."""
from datetime import datetime
from app.adapters.telegram.texts import car_price

G_MONTHS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _jalali(year: int, month: int, day: int) -> tuple[int, int, int]:
    gy, gm, gd = year - 1600, month - 1, day - 1
    leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
    total = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    total += sum(G_MONTHS[:gm]) + (1 if leap and gm > 1 else 0) + gd
    jday = total - 79
    cycle, jday = divmod(jday, 12053)
    jy = 979 + 33 * cycle + 4 * (jday // 1461)
    jday %= 1461
    if jday >= 366:
        jy += (jday - 1) // 365
        jday = (jday - 1) % 365
    if jday < 186:
        jm, jd = jday // 31 + 1, jday % 31 + 1
    else:
        jm, jd = (jday - 186) // 30 + 7, (jday - 186) % 30 + 1
    return jy, jm, jd


def fa(value: str) -> str:
    """Return a Persian weekday and date."""
    date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    year, month, day = _jalali(date.year, date.month, date.day)
    weekday = car_price.PERSIAN_WEEKDAYS[date.weekday()]
    return f"{weekday} {day} {car_price.PERSIAN_MONTHS[month - 1]}"
