import io

from PIL import Image

from app.core import car_images as ci

PAGE = (
    'x api2.zoomit.ir/media/logo-wepod-zomit-1 '
    'api2.zoomit.ir/media/car-a-2023-inside-aa '
    'api2.zoomit.ir/media/car-a-2023-aa '
    'https:\\/\\/api2.zoomit.ir\\/media\\/car-a-2023-back-bb '
    'api2.zoomit.ir/media/car-a-2023-front-side-cc '
    'api2.zoomit.ir/media/untitled-1-dd '
    'api2.zoomit.ir/media/car-a-2023-aa '
    'api2.zoomit.ir/media/car-a-2023-side-ee '
    'api2.zoomit.ir/media/car-a-2023-top-ff'
)


def test_media_names_dedup_and_escaped_slash():
    names = ci.media_names(PAGE)
    assert names.count("car-a-2023-aa") == 1
    assert "car-a-2023-back-bb" in names


def test_pick_skips_logos_and_limits():
    got = ci.pick(PAGE)
    assert len(got) == ci.MAX_PHOTOS
    assert not any("logo" in n or "untitled" in n for n in got)


def test_pick_order_main_first_inside_last():
    got = ci.pick(PAGE)
    assert got[0] == "car-a-2023-aa"
    assert got[1] == "car-a-2023-front-side-cc"
    assert "car-a-2023-inside-aa" not in got


def test_old_style_names_keep_page_order():
    page = "api2.zoomit.ir/media/2018-12-u1-a api2.zoomit.ir/media/2018-12-u2-b"
    assert ci.pick(page) == ["2018-12-u1-a", "2018-12-u2-b"]


def test_to_jpeg_from_png():
    buf = io.BytesIO()
    Image.new("RGBA", (8, 8), (255, 0, 0, 255)).save(buf, "PNG")
    assert ci.to_jpeg(buf.getvalue())[:2] == b"\xff\xd8"
