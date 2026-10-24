"""اجرای یک تابع دیتابیس با اتصال کوتاه‌مدت."""
from app.config import Settings
from app.data import db


def run(settings: Settings, fn, *args):
    conn = db.connect(settings.db_path)
    try:
        return fn(conn, *args)
    finally:
        conn.close()
