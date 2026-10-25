"""One video page per source photo."""
from app.adapters.telegram.texts import daily_prices as t
from app.core import daily_video


def test_one_page_per_group():
    pages = daily_video.split_pages(
        [list(range(5)), list(range(7)), list(range(2))])
    assert [len(p) for p in pages] == [5, 7, 2]


def test_big_group_splits_evenly_and_keeps_boundary():
    big = list(range(daily_video.PAGE_ROWS + 1))
    pages = daily_video.split_pages([big, list(range(3))])
    assert len(pages) == 3
    assert abs(len(pages[0]) - len(pages[1])) <= 1
    assert sum(len(p) for p in pages[:2]) == len(big)
    assert len(pages[2]) == 3


def test_empty_group_is_skipped():
    assert daily_video.split_pages([[], [1, 2]]) == [[1, 2]]


def test_render_frames_changes_page_per_photo():
    rows = [
        {"name": f"Car {i}", "year": 1404, "price_m": 1000 + i,
         "change_m": 0, "photo": 1 + i % 2}
        for i in range(4)
    ]
    frames = list(daily_video.render_frames(rows, "x", t))
    assert len(frames) == 6  # 2 photos x (2 rows + 1 empty start frame)
