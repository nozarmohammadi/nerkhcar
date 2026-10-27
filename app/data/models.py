"""ساختار داده‌ها."""
from dataclasses import dataclass


@dataclass
class Admin:
    tg_id: int
    role: str
    pw_hash: str | None
    must_change: int
    failed_count: int
    locked_until: str | None
    session_until: str | None
    is_active: int
    created_at: str


@dataclass
class Price:
    id: int
    trim_id: int
    year: int
    low: int
    high: int
    confidence: str
    status: str
    updated_at: str
    confirmed_at: str | None
    entered_by: int | None
    source: str = "photo"
