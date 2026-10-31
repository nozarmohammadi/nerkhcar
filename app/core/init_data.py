"""Validate Telegram Mini App initData (HMAC-SHA256). No Telegram imports."""
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

MAX_AGE_SECONDS = 24 * 3600
MAX_FUTURE_SECONDS = 60
MAX_LENGTH = 4096


def _expected_hash(fields: dict, bot_token: str) -> str:
    """HMAC of the sorted key=value lines, as the Telegram docs describe."""
    lines = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    return hmac.new(key, lines.encode(), hashlib.sha256).hexdigest()


def _parse(init_data: str):
    """Split the query string into a dict; None if it is malformed."""
    try:
        pairs = parse_qsl(init_data, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        return None
    return dict(pairs)


def _fresh(fields: dict, now: float, max_age: int) -> bool:
    """True if auth_date is recent and not in the future."""
    try:
        age = now - int(fields["auth_date"])
    except (KeyError, ValueError):
        return False
    return -MAX_FUTURE_SECONDS <= age <= max_age


def _user_id(fields: dict):
    """Read the numeric Telegram user id from the user JSON; None if bad."""
    try:
        user = json.loads(fields["user"])
    except (KeyError, ValueError, RecursionError):
        return None
    uid = user.get("id") if isinstance(user, dict) else None
    if isinstance(uid, int) and not isinstance(uid, bool) and uid > 0:
        return uid
    return None


def validate(init_data, bot_token, now=None, max_age=MAX_AGE_SECONDS):
    """Return the Telegram user id if initData is genuine and fresh, else None."""
    if not init_data or not bot_token or len(init_data) > MAX_LENGTH:
        return None
    fields = _parse(init_data)
    if fields is None:
        return None
    given = fields.pop("hash", "")
    expected = _expected_hash(fields, bot_token)
    if not hmac.compare_digest(given.encode(), expected.encode()):
        return None
    if not _fresh(fields, time.time() if now is None else now, max_age):
        return None
    return _user_id(fields)
