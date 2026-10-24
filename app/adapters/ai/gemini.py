"""خواندن عکس جدول با Gemini (فقط شبکه؛ بدون منطق جدول)."""
import base64
import logging

import aiohttp

from app.core.table_prompt import PROMPT

log = logging.getLogger("nerkhcar.ai")
BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
TIMEOUT = aiohttp.ClientTimeout(total=90)


def build_body(image: bytes, mime: str) -> dict:
    data = base64.b64encode(image).decode("ascii")
    return {
        "contents": [{"parts": [
            {"text": PROMPT},
            {"inline_data": {"mime_type": mime, "data": data}},
        ]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
        },
    }


def reply_text(data: dict) -> str:
    try:
        parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError):
        return ""
    return "".join(p.get("text", "") for p in parts if isinstance(p, dict))


def _result(status: int, data: dict) -> tuple[str, str]:
    if status == 200:
        text = reply_text(data)
        return ("ok", text) if text else ("empty", "")
    log.warning("پاسخ ناموفق هوش مصنوعی: %s", status)
    names = {429: "rate_limit", 503: "overloaded"}
    return names.get(status, f"http_{status}"), ""


def make_extractor(key: str):
    async def extract(image: bytes, mime: str, model: str) -> tuple[str, str]:
        if not key:
            return "no_key", ""
        headers = {"x-goog-api-key": key, "content-type": "application/json"}
        url = f"{BASE}{model}:generateContent"
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=TIMEOUT) as s:
                async with s.post(url, json=build_body(image, mime)) as r:
                    return _result(r.status, await r.json())
        except Exception as exc:
            log.warning("خطای اتصال به هوش مصنوعی: %s", type(exc).__name__)
            return "net", ""

    return extract
