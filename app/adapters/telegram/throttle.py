"""Per-user rate limit (anti-spam) as an aiogram outer middleware."""
import logging
import time
from collections import deque

from aiogram import BaseMiddleware

from app.adapters.telegram.texts import throttle as t

log = logging.getLogger("nerkhcar")

OK = "ok"
NOTIFY = "notify"
DROP = "drop"
_PRUNE_AT = 5000


class ThrottleMiddleware(BaseMiddleware):
    """Allow max_events per window seconds per user; then block for block seconds."""

    def __init__(self, max_events=15, window=10.0, block=10.0,
                 exempt_ids=(), clock=time.monotonic):
        self.max_events = max_events
        self.window = window
        self.block = block
        self.exempt = set(exempt_ids)
        self.clock = clock
        self._hits = {}
        self._blocked_until = {}

    def _prune(self, now):
        for uid in list(self._hits):
            hits = self._hits[uid]
            idle = not hits or hits[-1] < now - self.window
            if idle and self._blocked_until.get(uid, 0) <= now:
                self._hits.pop(uid, None)
                self._blocked_until.pop(uid, None)

    def check(self, user_id):
        """Return OK, NOTIFY (first blocked event) or DROP."""
        if user_id in self.exempt:
            return OK
        now = self.clock()
        if len(self._hits) > _PRUNE_AT:
            self._prune(now)
        until = self._blocked_until.get(user_id)
        if until is not None:
            if now < until:
                return DROP
            del self._blocked_until[user_id]
        hits = self._hits.setdefault(user_id, deque())
        while hits and hits[0] <= now - self.window:
            hits.popleft()
        hits.append(now)
        if len(hits) > self.max_events:
            hits.clear()
            self._blocked_until[user_id] = now + self.block
            return NOTIFY
        return OK

    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if user is None:
            return await handler(event, data)
        verdict = self.check(user.id)
        if verdict == OK:
            return await handler(event, data)
        if verdict == NOTIFY:
            log.warning("user throttled")
            try:
                await event.answer(t.THROTTLED)
            except Exception as exc:
                log.error("throttle notice failed: %s", type(exc).__name__)
        return None
