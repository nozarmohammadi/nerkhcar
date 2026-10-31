"""Cooldown gate so unexpected-error alerts to the owner never flood."""
import time


class ErrorAlertGate:
    """Allow one owner alert per cooldown period (seconds)."""

    def __init__(self, cooldown: float = 600.0, clock=time.monotonic):
        self.cooldown = cooldown
        self.clock = clock
        self._last = None

    def allow(self) -> bool:
        now = self.clock()
        if self._last is not None and now - self._last < self.cooldown:
            return False
        self._last = now
        return True
