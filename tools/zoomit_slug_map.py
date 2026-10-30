"""One-off map: trim id -> Zoomit car slug.

EXACT: same car and same trim. FAMILY: same car family, but the trim
differs or the match is unsure; needs a human check before display.
"""

EXACT_TEXT = """
9 ikco-arisun-2; 13 mvm-x22-pro; 14 mvm-x33-cross; 15 mvm-x5; 17 mvm-x77;
38 dongfeng-ix5-dignity-prime; 48 saipa-saina-s; 56 saipa-shahin-plus-at;
75 fidelity-prestige; 76 lamari-echo; 77 lamari-eama; 78 lamari-neo;
445 lamari-eama-hev; 85 haima-haima-7x; 86 haima-8s; 87 haima-s5;
99 saipa-quick-gx; 102 saipa-quick-s; 22807 saipa-quick-r;
103 kmc-a5; 104 jac-kmc-j7; 105 kmc-sr3; 107 jac-kmc-t8; 108 jac-kmc-t9;
110 kmc-eagle; 117 audi-q5-e-tron; 123 skoda-karoq-2023;
127 skoda-superb-2023; 171 mercedes-benz-glb-200-2024;
202 byd-qin-plus-dm-i; 204 byd-dolphin; 223 gwm-tank-300;
234 toyota-levin-hybrid-2024; 237 toyota-bz3; 239 toyota-bz3x;
238 toyota-corolla-cross-hev-2024; 253 toyota-bz5;
275 gac-gs3-emzoom-2023; 286 changan-eado-ev460; 288 changan-cs35-plus;
291 changan-cs55-plus; 295 changan-uni-t; 299 dongfeng-shine-max;
323 ssangyong-torres; 333 suzuki-ciaz-2023; 337 suzuki-baleno-2024;
340 suzuki-fronx-2024; 344 suzuki-jimny-2019;
345 suzuki-jimny-5-door-2023; 369 volkswagen-t-roc-2024;
433 kia-k3-sedan-2024; 437 kia-k5-optima-2023; 470 mazda-cx30;
476 mazda-ez-60-erev; 486 nissan-sylphy-e-power; 498 nissan-teana-2024;
83 nissan-terra-maanian-khodro; 501 volvo-xc70-2025; 510 haval-h9-2024;
520 honda-city-sedan-2024; 524 honda-hr-v-ehev-2024;
527 honda-civic-sedan-2024; 528 honda-cr-v-2024; 529 honda-zr-v-2024;
531 honda-accord-ephev-2024; 533 honda-civic-type-r-2024;
537 hyundai-kona-2024; 8805 peugeot-206-type2; 8826 peugeot-206-sd-v8;
8834 peugeot-206sd-v2; 8847 peugeot-405-glx-25634;
8867 peugeot-405-slx-22009; 8884 peugeot-pars-automatic-28706;
8936 renault-tondar-90-e1; 8941 renault-tondar-90-e0; 8958 ikco-samand-lx;
8962 ikco-samand-lx-ef7-gasoline; 9019 saipa-changan-cs35-auto;
9021 saipa-changan-cs35-maual; 9026 saipa-ario-manual-1600;
22742 ikco-runna-lx-61006; 22753 ikco-samand-soren-elx-ef7-57511;
22800 saipa-saina-ex; 22699 haima-s7-automatic;
8794 haima-s7-turbo-automatic
"""

FAMILY_TEXT = """
10 saipa-atlas; 11 saipa-atlas; 16 mvm-x55-2018; 36 ikco-dena-plus;
53 saipa-shahin; 54 saipa-shahin; 55 saipa-shahin-at;
62 foton-tunland; 92 peugeot-207i-manual-60002; 100 saipa-quick-gx-r;
116 audi-q4-50-e-tron; 125 skoda-octavia-2023; 139 mg-gt-2024;
166 baic-bj40; 167 mercedes-benz-a180-l-2024;
172 mercedes-benz-c200-l-2024; 230 toyota-corolla-2023;
231 toyota-corolla-hybrid-2024; 248 toyota-camry-hev-2025;
259 toyota-avalon-2019; 263 toyota-prado-j250-2025;
265 toyota-land-cruiser-j300-2025; 277 gac-emkoo-2022;
280 gac-empow-2021; 22767 changan-cs55-plus;
321 ssangyong-tivoli-2018-elite; 322 ssangyong-korando--2018;
335 suzuki-swift-mhev-2024; 377 volkswagen-tiguan-2018;
432 kia-sportage-2023; 447 lexus-es200-2024; 474 mazda-ez-6-ev;
472 mazda-3-2024; 483 mini-cooper-2018; 491 nissan-altima-2019;
497 nissan-xtrail-2018; 499 nissan-patrol-2025; 508 haval-h6;
536 hyundai-elantra-2023; 540 hyundai-sonata-2019;
542 hyundai-santa-fe-2019; 8799 peugeot-2008;
8844 peugeot-207i-sedan-60302; 22713 peugeot-207i-manual-60002;
22716 peugeot-207i-manual-60002; 8994 ikco-arisun-dual-feul;
9030 saipa-ario-elegant; 9033 saipa-111; 9038 saipa-111; 9041 saipa-111;
9044 saipa-131; 9048 saipa-131; 9049 saipa-131; 9050 saipa-131;
9052 saipa-131; 9054 saipa-132; 9060 saipa-132; 9063 saipa-132;
22735 ikco-dena; 22736 ikco-dena-plus; 22737 ikco-dena-plus;
22738 ikco-dena-plus; 22739 ikco-dena-plus;
22752 ikco-samand-soren-plus-mt; 22799 saipa-saina-s
"""


def _parse(text):
    out = {}
    for chunk in text.replace("\n", " ").split(";"):
        parts = chunk.split()
        if parts:
            out[int(parts[0])] = parts[1]
    return out


def exact():
    return _parse(EXACT_TEXT)


def family():
    return _parse(FAMILY_TEXT)


FAMILY_TEXT_2 = """
9099 saipa-tiba; 9105 saipa-tiba; 9113 saipa-tiba-2; 9120 saipa-tiba-2;
9122 saipa-zamyad-zagros; 9135 kia-cerato-2000-auto-optional;
9136 kia-cerato-1600-manual-optional; 9137 kia-cerato-1600-manual;
9149 saipa-padra; 9155 saipa-zamyad-24-dual-feul;
9156 saipa-zamyad-24-gasoline; 9157 saipa-zamyad-24-gasoline;
9161 saipa-zamyad-24-dual-feul; 9162 saipa-zamyad-24-gasoline;
9178 saipa-zamyad-karoon; 9182 peugeot-301; 9184 peugeot-508-2019;
22696 haima-s5; 22697 haima-s5; 22698 haima-s5;
8842 peugeot-207i-automatic-60102; 8845 peugeot-207i-automatic-60102;
22712 peugeot-207i-manual-60002; 22713 peugeot-207i-manual-60002;
22715 peugeot-207i-manual-60002; 8861 peugeot-405-glx-25634;
8880 peugeot-pars-lx; 8882 peugeot-pars-lx; 8887 peugeot-pars-lx;
8978 ikco-samand-lx; 8983 ikco-samand-lx; 8993 ikco-samand-lx;
22743 ikco-runna-lx-61006; 22751 ikco-samand-soren-plus-mt;
22763 changan-cs35-plus; 22764 changan-cs35-plus;
22771 saipa-atlas; 22772 saipa-atlas; 22801 saipa-saina-se-auto;
9000 ikco-arisun-2; 8828 peugeot-206-sd-v8; 8807 peugeot-206-type2;
8781 peugeot-roa; 8785 peugeot-roa
"""


def family():
    out = _parse(FAMILY_TEXT)
    out.update(_parse(FAMILY_TEXT_2))
    return out
