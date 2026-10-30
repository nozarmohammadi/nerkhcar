"""Texts and group map for the 'technical specs' button."""

SOON = "مشخصات فنی به‌زودی اضافه می‌شود 🛠"
PICK_GROUP = "دسته را انتخاب کن" + "\u00a0" * 40
PICK_CAR = "خودرو را انتخاب کن"
MISSING = "مشخصات این خودرو پیدا نشد 🙏"
BTN_GROUP = "{name} | {n}"
TITLE = "📋 مشخصات فنی {name}"
LINE = "{label}: {value}"
OTHER = "سایر"
HEAD = ("مشخصه", "مقدار")
# Banner theme index per group index (order of GROUPS); last = neutral.
THEMES = (0, 1, 2, 3, 4, 5, -1)

# Group name -> source slug prefixes (first part of the Zoomit slug).
GROUPS = (
    ("سایپا", ("saipa",)),
    ("ایران\u200cخودرو", ("ikco", "peugeot")),
    ("چینی", (
        "baic", "byd", "changan", "dongfeng", "fidelity", "foton", "gac",
        "gwm", "haima", "haval", "jac", "kmc", "lamari", "mg", "mvm")),
    ("ژاپنی", ("honda", "lexus", "mazda", "nissan", "suzuki", "toyota")),
    ("کره\u200cای", ("hyundai", "kia", "ssangyong")),
    ("اروپایی", (
        "audi", "mercedes", "mini", "renault", "skoda", "volkswagen",
        "volvo")),
)

# (specs_json key, Persian label), in display order. Empty values are skipped.
LABELS = (
    ("series", "سری تولید"),
    ("origin", "نوع تولید و عرضه"),
    ("distributor", "شرکت عرضه‌کننده"),
    ("body_type", "نوع بدنه"),
    ("dimensions", "ابعاد بدنه"),
    ("wheelbase", "فاصله بین دو محور"),
    ("seats", "تعداد سرنشین"),
    ("doors", "تعداد درها"),
    ("trunk", "حجم صندوق عقب"),
    ("weight", "وزن"),
    ("powertrain", "نوع قوای محرکه"),
    ("aspiration", "نوع تنفس موتور"),
    ("engine_layout", "چیدمان موتور"),
    ("engine_model", "مدل موتور"),
    ("displacement", "حجم موتور"),
    ("cylinders", "تعداد سیلندر"),
    ("valves", "تعداد سوپاپ"),
    ("power", "قدرت"),
    ("torque", "گشتاور"),
    ("accel_0_100", "شتاب ۰ تا ۱۰۰"),
    ("top_speed", "حداکثر سرعت"),
    ("fuel_city", "مصرف سوخت شهری"),
    ("fuel_highway", "مصرف سوخت بزرگراهی"),
    ("fuel_combined", "مصرف سوخت ترکیبی"),
    ("tank", "حجم باک"),
    ("gearbox", "گیربکس"),
    ("cvt", "گیربکس CVT"),
    ("gears", "تعداد دنده"),
    ("gearbox_features", "ویژگی‌های گیربکس"),
    ("drive", "سیستم محرک"),
    ("chassis", "شاسی"),
    ("steering", "فرمان"),
    ("suspension_front", "تعلیق و ترمز جلو"),
    ("suspension_rear", "تعلیق عقب"),
)
