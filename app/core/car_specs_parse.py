"""Parse a Zoomit car page into a flat specs dict. Pure functions, no network."""
import html as html_lib
import json
import re
from pathlib import Path

_LABELS_PATH = Path(__file__).resolve().parent.parent / "data" / "zoomit_labels.json"


def _norm(s):
    """Match key only: drop ZWNJ so labels compare reliably."""
    return s.replace("\u200c", "").strip()


def _load():
    raw = json.loads(_LABELS_PATH.read_text(encoding="utf-8"))
    labels = {_norm(k): v for k, v in raw["labels"].items()}
    sections = {_norm(s) for s in raw["sections"]}
    return labels, sections, _norm(raw["start"]), _norm(raw["stop"])


LABELS, SECTIONS, START, STOP = _load()


def html_to_text(page):
    page = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", page, flags=re.S)
    text = re.sub(r"<[^>]+>", "\n", page)
    text = html_lib.unescape(text)
    return re.sub(r"\n\s*\n+", "\n", text)


def _first_int(value):
    m = re.search(r"\d+", value or "")
    return int(m.group()) if m else None


def _fix_cylinders(out):
    """Zoomit sometimes swaps cylinders and valves (e.g. 16 and 4)."""
    cyl = _first_int(out.get("cylinders"))
    val = _first_int(out.get("valves"))
    if cyl is None or val is None:
        return
    if cyl > 12 and val <= 8:
        out["cylinders"], out["valves"] = out["valves"], out["cylinders"]
        out["note"] = "cylinders_valves_swapped"
    elif cyl == 12 and val <= 8:
        out["note"] = "cylinders_valves_suspect"


def parse_zoomit_text(text):
    raw = [x.strip() for x in text.splitlines()]
    raw = [x for x in raw if x]
    keys = [_norm(x) for x in raw]
    if START not in keys:
        return {}
    begin = keys.index(START)
    parts = {}
    cur = None
    for key, line in zip(keys[begin:], raw[begin:]):
        if key == STOP:
            break
        if key in SECTIONS:
            cur = None
            continue
        if key in LABELS:
            cur = LABELS[key]
            parts.setdefault(cur, [])
            continue
        if cur:
            parts[cur].append(line)
    out = {k: " ".join(v) for k, v in parts.items() if v}
    _fix_cylinders(out)
    return out
