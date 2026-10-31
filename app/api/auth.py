"""Telegram initData auth for the API. Header: Authorization: tma <initData>."""
import logging

from aiohttp import web

from app.core.init_data import validate

log = logging.getLogger("nerkhcar.api")
PREFIX = "tma "
NO_STORE = {"Cache-Control": "no-store"}


def user_id_from_request(request: web.Request):
    """Return the verified Telegram user id, or None."""
    header = request.headers.get("Authorization", "")
    if not header.startswith(PREFIX):
        return None
    return validate(header[len(PREFIX):].strip(), request.app["bot_token"])


async def me(request: web.Request) -> web.Response:
    """Tell the mini-app who the verified user is."""
    if not request.app["bot_token"]:
        log.error("api auth: bot token is not configured")
        return web.json_response({"status": "error"}, status=503, headers=NO_STORE)
    user_id = user_id_from_request(request)
    if user_id is None:
        return web.json_response({"status": "unauthorized"}, status=401, headers=NO_STORE)
    return web.json_response({"ok": True, "user_id": user_id}, headers=NO_STORE)
