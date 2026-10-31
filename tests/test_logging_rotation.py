"""Tests that file logging is rotating and bounded."""
import logging
from logging.handlers import RotatingFileHandler

from app.logging_setup import setup_logging


def test_file_handler_is_rotating_and_bounded(tmp_path):
    root = logging.getLogger()
    saved = list(root.handlers)
    try:
        setup_logging(tmp_path)
        handlers = [h for h in root.handlers if isinstance(h, RotatingFileHandler)]
        assert len(handlers) == 1
        h = handlers[0]
        assert h.maxBytes == 1_000_000
        assert h.backupCount == 5
        assert (tmp_path / "nerkhcar.log").exists()
    finally:
        for h in list(root.handlers):
            h.close()
        root.handlers.clear()
        root.handlers.extend(saved)
