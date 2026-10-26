"""Build the result text of the 'my car' estimate (pure logic)."""
from app.core import daily_text

BANDS = (("quick_sale", "BAND_QUICK"), ("fair", "BAND_FAIR"),
         ("listing", "BAND_LISTING"))


def round_m(value: float) -> int:
    """Round to a friendly number: 5 above 1000, otherwise 1."""
    step = 5 if value >= 1000 else 1
    return int(round(value / step) * step)


def _num(value: float) -> str:
    return daily_text.fa(f"{round_m(value):,}")


def build_text(result: dict, name: str, year: int, texts) -> str:
    """Result text; the caller handles non-ok statuses."""
    lines = [
        texts.RESULT_TITLE,
        texts.CAR_LINE.format(name=name, year=daily_text.fa(year)),
        texts.UNIT_LINE,
        "",
    ]
    for key, label in BANDS:
        low, high = result[key]
        lines.append(texts.BAND_LINE.format(
            label=getattr(texts, label), low=_num(low), high=_num(high)))
    if result.get("warn_above_zero"):
        lines += ["", texts.WARN_ZERO]
    return "\n".join(lines + ["", texts.DISCLAIMER])
