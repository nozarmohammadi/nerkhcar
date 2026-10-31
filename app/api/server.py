"""Tiny read-only JSON API (aiohttp), bound to localhost only."""
import logging
import os
import sqlite3
from pathlib import Path

from aiohttp import web

from app.api import auth, fx, prices
from app.api.db_ro import connect_ro
from app.config import load_settings

log = logging.getLogger("nerkhcar.api")
BASE = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB = BASE / "data" / "nerkhcar.db"
HOST = "127.0.0.1"
PORT = 8790
NO_STORE = {"Cache-Control": "no-store"}


async def health(request: web.Request) -> web.Response:
    return web.json_response({"ok": True}, headers=NO_STORE)


async def _serve(request: web.Request, reader) -> web.Response:
    """Run a read-only reader(conn) and return its dict as JSON."""
    try:
        conn = connect_ro(request.app["db_path"])
        try:
            data = reader(conn)
        finally:
            conn.close()
    except sqlite3.Error as exc:
        log.error("api db error: %s", type(exc).__name__)
        return web.json_response({"status": "error"}, status=503, headers=NO_STORE)
    return web.json_response(data, headers=NO_STORE)


async def daily_prices(request: web.Request) -> web.Response:
    return await _serve(request, prices.daily)


async def fx_prices(request: web.Request) -> web.Response:
    return await _serve(request, fx.latest)


def build_app(db_path=DEFAULT_DB, bot_token="") -> web.Application:
    app = web.Application()
    app["db_path"] = str(db_path)
    app["bot_token"] = bot_token
    app.router.add_get("/api/health", health)
    app.router.add_get("/api/prices/daily", daily_prices)
    app.router.add_get("/api/fx", fx_prices)
    app.router.add_get("/api/me", auth.me)
    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    db_path = os.environ.get("NERKHCAR_DB", str(DEFAULT_DB))
    token = load_settings().bot_token
    web.run_app(build_app(db_path, token), host=HOST, port=PORT)
