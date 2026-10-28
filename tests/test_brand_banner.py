from io import BytesIO

from PIL import Image

from app.core import brand_banner


def test_banner_is_png_with_fixed_size():
    data = brand_banner.render("هیوندای")
    assert data.startswith(b"\x89PNG")
    assert Image.open(BytesIO(data)).size == (brand_banner.WIDTH, brand_banner.HEIGHT)


def test_long_name_still_renders():
    assert brand_banner.render("نام خیلی خیلی بلند " * 6).startswith(b"\x89PNG")
