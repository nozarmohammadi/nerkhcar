"""Video frame planning and rendering for the daily price table."""
from io import BytesIO

from PIL import Image

from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_video


def _rows(n: int) -> list[dict]:
    return [
        {"name": f"Car {i}", "year": 1404, "price_m": 1000 + i,
         "change_m": 0, "photo": 1 + i % 2}
        for i in range(n)
    ]


def test_split_pages_sizes():
    pages = daily_video.split_pages([list(range(65))])
    assert len(pages) == 3
    assert sum(len(p) for p in pages) == 65
    assert max(len(p) for p in pages) <= daily_video.PAGE_ROWS


def test_split_pages_edges():
    assert daily_video.split_pages([]) == []
    assert len(daily_video.split_pages([list(range(20))])) == 1


def test_frame_plan_counts_and_length():
    pages = daily_video.split_pages([list(range(70))])
    plan = daily_video.frame_plan(pages)
    assert len(plan) == 70 + len(pages)
    assert plan[-1][2] == daily_video.END_HOLD_SEC
    assert sum(sec for _, _, sec in plan) < 60


def test_render_frames_png_size():
    frames = list(daily_video.render_frames(_rows(3), "x", t))
    assert len(frames) == 5  # 2 photos: (2 rows + 1) + (1 row + 1)
    png, _ = frames[-1]
    assert png[:4] == b"\x89PNG"
    assert Image.open(BytesIO(png)).size == daily_video.OUT_SIZE
