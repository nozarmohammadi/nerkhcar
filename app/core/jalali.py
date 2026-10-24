"""تبدیل تاریخ میلادی به شمسی. بدون تلگرام."""

_CUM_DAYS = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)


def to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    """نتیجه: (سال، ماه، روز) شمسی."""
    if gy > 1600:
        jy, gy = 979, gy - 1600
    else:
        jy, gy = 0, gy - 621
    leap_year = gy + 1 if gm > 2 else gy
    days = (365 * gy + (leap_year + 3) // 4 - (leap_year + 99) // 100
            + (leap_year + 399) // 400 - 80 + gd + _CUM_DAYS[gm - 1])
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        return jy, 1 + days // 31, 1 + days % 31
    return jy, 7 + (days - 186) // 30, 1 + (days - 186) % 30
