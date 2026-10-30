"""Download car photos from Zoomit into data/car_images/<slug>/N.jpg. Resumable.

Usage: PYTHONPATH=. venv/bin/python tools/zoomit_fetch_images.py [slug ...]
No slug given: all reviewed slugs. Never writes to the database.
"""
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

from app.core import car_images as ci

PAGE = "https://www.zoomit.ir/product/"
MEDIA = "https://api2.zoomit.ir/media/"
OUT = Path("data/car_images")
DB = "data/nerkhcar.db"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=25).read()


def reviewed_slugs():
    con = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    sql = "select distinct source_slug from car_specs where reviewed=1 order by 1"
    rows = con.execute(sql).fetchall()
    con.close()
    return [r[0] for r in rows]


def save_slug(slug):
    """Download up to MAX_PHOTOS photos of one car; return how many."""
    page = get(PAGE + slug + "/").decode("utf-8", "ignore")
    names = ci.pick(page)
    folder = OUT / slug
    folder.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(names, 1):
        time.sleep(3)
        data = get(MEDIA + name + "?w=1080&q=75")
        (folder / f"{i}.jpg").write_bytes(ci.to_jpeg(data))
    return len(names)


def main(slugs):
    for slug in slugs or reviewed_slugs():
        if (OUT / slug / "1.jpg").exists():
            continue
        try:
            count = save_slug(slug)
        except Exception as exc:
            print(slug, "FAIL", repr(exc)[:80], flush=True)
            continue
        print(slug, count, flush=True)
        time.sleep(3)
    print("DONE", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
