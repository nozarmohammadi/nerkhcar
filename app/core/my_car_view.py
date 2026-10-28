"""Build the result text of the 'my car' estimate (pure logic)."""
from app.core import daily_text

MILLION = 1_000_000
LABELS = ("BAND_QUICK", "BAND_FAIR", "BAND_LISTING")


def three_values(result: dict) -> tuple[float, float, float]:
    """Lowest, approximate (fair midpoint), highest; million toman."""
    return (result["quick_sale"][0], sum(result["fair"]) / 2,
            result["listing"][1])


def round_m(value: float) -> int:
    """Round to a friendly number: 5 above 1000, otherwise 1."""
    step = 5 if value >= 1000 else 1
    return int(round(value / step) * step)


def _num(value: float) -> str:
    """Full toman with separators, in Persian digits."""
    return daily_text.fa(f"{round_m(value) * MILLION:,}")


def build_text(result: dict, name: str, year: int, texts) -> str:
    """Result text; the caller handles non-ok statuses."""
    lines = [
        texts.RESULT_TITLE,
        texts.CAR_LINE.format(name=name, year=daily_text.fa(year)),
        texts.UNIT_LINE,
        "",
    ]
    for label, value in zip(LABELS, three_values(result)):
        lines.append(texts.BAND_LINE.format(
            label=getattr(texts, label), value=_num(value)))
    if result.get("warn_above_zero"):
        lines += ["", texts.WARN_ZERO]
    if result.get("confidence_low"):
        lines += ["", texts.LOW_CONFIDENCE]
    return "\n".join(lines + ["", texts.DISCLAIMER])
