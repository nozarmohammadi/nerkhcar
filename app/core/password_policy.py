"""قانون رمز ادمین."""
MIN_LENGTH = 10


def check_policy(password: str) -> str | None:
    """None یعنی رمز قابل قبول است؛ در غیر این صورت کد خطا."""
    if len(password) < MIN_LENGTH:
        return "too_short"
    if not any(c.isalpha() for c in password):
        return "no_letter"
    if not any(c.isdigit() for c in password):
        return "no_digit"
    return None
