"""Static checks for the mini-app shell (webapp/)."""
import re
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "webapp"
FILES = ["index.html", "style.css", "texts.js", "app.js"]
PERSIAN = re.compile(r"[\u0600-\u06FF]")


def _read(name):
    return (WEB / name).read_text(encoding="utf-8")


def test_files_exist_and_are_short():
    for name in FILES:
        assert len(_read(name).splitlines()) <= 200, name


def test_html_is_persian_rtl_mobile():
    html = _read("index.html")
    assert 'lang="fa"' in html and 'dir="rtl"' in html
    assert "width=device-width" in html
    assert "telegram.org/js/telegram-web-app.js" in html


def test_persian_text_only_in_texts_file():
    for name in ("index.html", "style.css", "app.js"):
        assert not PERSIAN.search(_read(name)), name
    assert PERSIAN.search(_read("texts.js"))


def test_dark_mode_and_telegram_theme():
    css = _read("style.css")
    assert "prefers-color-scheme: dark" in css
    assert "--tg-theme-bg-color" in css


def test_script_is_safe_and_light():
    js = _read("app.js")
    for bad in ("innerHTML", "localStorage", "eval(", "document.write"):
        assert bad not in js, bad


def test_menu_has_five_unique_ascii_routes():
    keys = re.findall(r'\["([a-z]+)",', _read("texts.js"))
    assert len(keys) == 5 and len(set(keys)) == 5
    assert keys[0] == "price"
