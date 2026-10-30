"""Brand banner colors follow the brand, not the table order."""
from app.core import brand_banner


def test_every_theme_has_three_colors():
    for theme in brand_banner.THEMES:
        assert len(theme) == 3
        for color in theme:
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)


def test_saipa_is_orange():
    red, green, blue = brand_banner.THEMES[0][1]
    assert red > green > blue


def test_iran_khodro_is_blue():
    red, green, blue = brand_banner.THEMES[1][1]
    assert blue > green > red


def test_chinese_is_red():
    red, green, blue = brand_banner.THEMES[2][1]
    assert red > green and red > blue


def test_themes_render_png():
    for index in (0, 1, 2, 5):
        png = brand_banner.render("سایپا", index)
        assert png[:4] == b"\x89PNG"
