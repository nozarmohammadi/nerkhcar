"""Fetch Zoomit car pages and parse specs. Resumable, writes only OUT.json.

Usage: PYTHONPATH=. venv/bin/python tools/zoomit_fetch_specs.py OUT.json slug|@file ...
Never touches the database.
"""
import json
import sys
import time
import urllib.request

from app.core import car_specs_parse as p

BASE = "https://www.zoomit.ir/product/"


def fetch(slug):
    req = urllib.request.Request(BASE + slug + "/", headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")


def read_slugs(args):
    slugs = []
    for arg in args:
        if arg.startswith("@"):
            slugs += open(arg[1:], encoding="utf-8").read().split()
        else:
            slugs.append(arg)
    return slugs


def load_results(out_path):
    try:
        return json.load(open(out_path, encoding="utf-8"))
    except Exception:
        return {}


def save_results(out_path, results):
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)


def get_specs(slug):
    """Return parsed specs, or None after printing the reason."""
    try:
        specs = p.parse_zoomit_text(p.html_to_text(fetch(slug)))
    except Exception as exc:
        print(slug, "FAIL", repr(exc)[:80], flush=True)
        return None
    if not specs:
        print(slug, "EMPTY", flush=True)
        return None
    return specs


def main(out_path, args):
    results = load_results(out_path)
    fails = []
    for slug in read_slugs(args):
        if slug in results:
            continue
        specs = get_specs(slug)
        if specs is None:
            fails.append(slug)
            continue
        results[slug] = specs
        save_results(out_path, results)
        print(slug, len(specs), specs.get("note", ""), flush=True)
        time.sleep(1.5)
    print("DONE ok", len(results), "failed", len(fails), fails, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
