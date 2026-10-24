"""تنظیمات مشترک تست‌ها: دیتابیس موقت برای هر تست."""
import pytest

from app.data import db


@pytest.fixture
def conn(tmp_path):
    path = tmp_path / "test.db"
    backups = tmp_path / "backups"
    backups.mkdir()
    db.migrate(path, backups)
    connection = db.connect(path)
    yield connection
    connection.close()
