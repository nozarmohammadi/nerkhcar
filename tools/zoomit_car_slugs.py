"""One-off helper: list car product slugs from the Zoomit sitemap.

Read-only. Writes one slug per line to the path given as argv[1].
"""
import re
import sys
import time
import urllib.request

INDEX = "https://www.zoomit.ir/product/zoobin-sitemap.xml"
PREFIXES = (
    "saipa-", "ikco-", "mvm-", "jac-", "changan-", "lamari-", "lamako-",
    "haval-", "greatwall-", "gwm-", "chery-", "byd-", "bmw-", "mercedes-benz-",
    "toyota-", "hyundai-", "kia-", "nissan-", "suzuki-", "mazda-", "honda-",
    "volvo-", "lexus-", "geely-", "fidelity-", "renault-", "volkswagen-",
    "skoda-", "land-rover-", "opel-", "citroen-", "peugeot-", "dena-",
    "audi-", "mg-", "gac-", "baic-", "bac-", "dongfeng-", "foton-",
    "jetour-", "kgm-", "ssangyong-", "haima-", "mini-cooper", "fiat-",
    "zamyad-", "pars-khodro-", "kmc-", "tesla-", "infinity-", "infiniti-",
    "bestune-", "forthing-", "maxus-", "dfsk-", "sinotruk-",
)


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")


def main(out_path):
    subs = re.findall(r"<loc>([^<]+)</loc>", get(INDEX))
    slugs = set()
    for sub in subs:
        slugs.update(re.findall(r"/product/([^/<]+)/", get(sub)))
        time.sleep(0.4)
    cars = sorted(s for s in slugs if s.startswith(PREFIXES))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(cars) + "\n")
    print("all slugs", len(slugs), "car slugs", len(cars))
    for p in PREFIXES:
        n = len([s for s in cars if s.startswith(p)])
        if n:
            print(p, n)


if __name__ == "__main__":
    main(sys.argv[1])
