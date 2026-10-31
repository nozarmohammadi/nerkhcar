"""Guard for the mini-app package (webapp_v2): fails when someone breaks its rules."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "webapp_v2"
CODE = [p for p in ROOT.rglob("*") if p.suffix in (".js", ".css", ".html")]
FA = re.compile("[\u0600-\u06FF]")
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")
BAD_JS = ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(")


def _text(path):
    return path.read_text(encoding="utf-8")


def test_files_exist():
    assert CODE, "webapp_v2 has no code files"


def test_max_200_lines():
    for p in CODE:
        assert len(_text(p).splitlines()) <= 200, f"{p.name} is over 200 lines"


def test_no_unsafe_dom():
    for p in ROOT.rglob("*.js"):
        for word in BAD_JS:
            assert word not in _text(p), f"{p.name} uses {word}"


def test_persian_only_in_texts():
    allowed = {"texts.js", "mock.js"}
    for p in CODE:
        if p.name not in allowed:
            assert not FA.search(_text(p)), f"Persian text outside texts.js: {p.name}"


def test_colors_only_in_tokens():
    for p in CODE:
        if p.name != "tokens.css":
            assert not COLOR.search(_text(p)), f"color literal outside tokens.css: {p.name}"


def test_icon_paths_only_in_icons():
    for p in ROOT.rglob("*.js"):
        if p.name not in ("icons.js", "ui.js"):
            assert "setAttribute('d'" not in _text(p), f"icon drawing outside ui.js: {p.name}"


def test_js_classes_defined_in_css():
    css = _text(ROOT / "css" / "components.css")
    used = set()
    for p in ROOT.rglob("*.js"):
        used |= set(re.findall(r"['\" ]((?:c|l)-[a-z0-9_-]+)", _text(p)))
    for name in used:
        assert "." + name in css, f"class {name} is not defined in components.css"


def test_only_telegram_external_script():
    html = _text(ROOT / "index.html")
    for src in re.findall(r'src="(https?://[^"]+)"', html):
        assert src.startswith("https://telegram.org/"), f"external script: {src}"
