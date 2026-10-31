"""Tests for initData validation and the /api/me endpoint."""
import asyncio
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl, urlencode

from aiohttp.test_utils import TestClient, TestServer

from app.api.server import build_app
from app.core.init_data import validate

TOKEN = "12345:fake-test-token"
NOW = 1_800_000_000


def make(fields, token=TOKEN):
    """Build a correctly signed initData string."""
    lines = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    digest = hmac.new(key, lines.encode(), hashlib.sha256).hexdigest()
    return urlencode({**fields, "hash": digest})


def fields(user_id=42, auth_date=NOW):
    user = json.dumps({"id": user_id, "first_name": "T"})
    return {"auth_date": str(auth_date), "query_id": "AAH", "user": user}


def test_valid_returns_user_id():
    assert validate(make(fields()), TOKEN, now=NOW + 10) == 42


def test_wrong_token_rejected():
    assert validate(make(fields(), "99999:other-token"), TOKEN, now=NOW) is None


def test_tampered_user_rejected():
    data = dict(parse_qsl(make(fields())))
    data["user"] = json.dumps({"id": 43})
    assert validate(urlencode(data), TOKEN, now=NOW) is None


def test_old_auth_date_rejected():
    assert validate(make(fields()), TOKEN, now=NOW + 25 * 3600) is None


def test_future_auth_date_rejected():
    assert validate(make(fields(auth_date=NOW + 600)), TOKEN, now=NOW) is None


def test_garbage_rejected():
    for bad in ("", "abc", "hash=zz", None, "a=1&hash=", "x" * 5000):
        assert validate(bad, TOKEN, now=NOW) is None


def test_missing_or_bad_user_rejected():
    no_user = {"auth_date": str(NOW)}
    bad_user = {"auth_date": str(NOW), "user": "[1,2]"}
    assert validate(make(no_user), TOKEN, now=NOW) is None
    assert validate(make(bad_user), TOKEN, now=NOW) is None


def _get(header, token=TOKEN):
    async def run():
        app = build_app(bot_token=token)
        async with TestClient(TestServer(app)) as client:
            headers = {"Authorization": header} if header else {}
            resp = await client.get("/api/me", headers=headers)
            return resp.status, await resp.json()
    return asyncio.run(run())


def test_me_ok():
    init = make(fields(user_id=7, auth_date=int(time.time())))
    assert _get("tma " + init) == (200, {"ok": True, "user_id": 7})


def test_me_unauthorized():
    assert _get(None)[0] == 401
    assert _get("Bearer abc")[0] == 401
    assert _get("tma garbage")[0] == 401


def test_me_without_token_is_503():
    init = make(fields(auth_date=int(time.time())))
    assert _get("tma " + init, token="")[0] == 503
