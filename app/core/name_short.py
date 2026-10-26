"""Shorten long car names so the price table stays narrow (pure logic)."""
import re

MAX_SHOWN = 24
PARENS = re.compile(r"\s*\([^)]*\)")


def short_name(name: str, limit: int = MAX_SHOWN) -> str:
    """Drop bracketed notes first; then cut at a word edge with an ellipsis."""
    if len(name) <= limit:
        return name
    plain = " ".join(PARENS.sub("", name).split()) or name
    if len(plain) <= limit:
        return plain
    cut = plain[:limit - 1]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip() + "\u2026"
