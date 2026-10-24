from app.adapters.ai import gemini
from app.adapters.telegram.texts import daily_prices as t


def test_503_is_overloaded():
    assert gemini._result(503, {}) == ("overloaded", "")


def test_429_and_500_unchanged():
    assert gemini._result(429, {}) == ("rate_limit", "")
    assert gemini._result(500, {}) == ("http_500", "")


def test_overloaded_has_message():
    assert "overloaded" in t.READ_ERRORS
