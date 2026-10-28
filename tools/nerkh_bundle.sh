#!/bin/bash
cd /opt/nerkhcar || exit 1
OUT=/root/Nerkh.txt
{
echo "# بستهٔ کامل پروژه نرخ‌کار - $(date '+%F %T')"
cat <<'HDR'

## دستور به هوش مصنوعی
تو مهندس نرم‌افزار ارشد هستی. من برنامه‌نویس نیستم. هر چیز باید کامل، قدم‌به‌قدم، قابل کپی‌پیست، به فارسی ساده و کوتاه باشد. حدس نزن؛ اگر نمی‌دانی بپرس. در انتهای هر پیام درصد پیشرفت چک‌لیست اصلی را بگو (در ابتدای پیام). بعد از هر قدم و هر تیک، خلاصهٔ کوتاه بده: انجام‌شده‌ها با ✅ و باقی‌مانده با ⬜.

## پروژه
ربات تلگرام «نرخ‌کار» (@nerkhcar_bot) در /opt/nerkhcar، کاربر nerkhcar، venv در /opt/nerkhcar/venv، دیتابیس data/nerkhcar.db، سرویس nerkhcar.service (MemoryMax=300M). ۳ دکمه: قیمت خودرو، ارز/سکه/طلا، قیمت خودروی من (فقط بازه). خودرو نمی‌فروشیم. بعد از ربات: کانال تلگرام، بعد بله. روی همین سرور پروژه‌های دیگر هم هست؛ به آن‌ها دست نزن. رم کم است (مرورگر بی‌سر یا کار سنگین ممنوع). توکن و رازها را هرگز از من نخواه؛ در grep فیلتر key نزن (فقط grep -v "AIza").

## قوانین کار
- هر بار فقط یک مرحله؛ بعد گزارش و منتظر تأیید. هر تغییر: بکاپ، تغییر، تست، گزارش. ریستارت فقط وقتی من بنویسم «ریستارت».
- قبل از دستور خطرناک (حذف، بازنویسی، force push) هشدار و تأیید.
- همهٔ دستورها در یک بلوک واحد برای کپی‌پیست؛ دستورهای خواندن کوتاه (حداکثر حدود ۵۰ خط خروجی).
- فایل جدید: بلوک با if [ -e فایل ]; then متوقف شد; else شروع شود. پچ فایل موجود: اسکریپت python3 که اول assert count(old)==1 برای همهٔ فایل‌ها را بررسی کند و بعد بنویسد. قبل از پچ بکاپ با نام جدید در backups/.
- قبل از commit سه چک سبز: pytest، tools/check_rules.py، tools/check_secrets.sh؛ با nohup در پس‌زمینه و خروجی در /tmp؛ تا «=== تمام ===» نیامده commit نزن.
- commit: git add فقط مسیرهای مشخص، قبل از آن git status --short؛ بعد commit و push origin dev.
- تست جدید در فایل جدا. کد جدید: کامنت و docstring انگلیسی؛ متن فارسی فقط در texts/.
- مرجع‌ها فقط دستی (اسکرپ ممنوع) و عددشان به کاربر نشان داده نشود؛ قیمت منقضی (>۷۲ ساعت) نمایش داده نشود؛ دروازهٔ کیفیت: اختلاف ≤۵٪ سبز، ۵ تا ۱۰٪ زرد، ۱۰ تا ۱۵٪ نارنجی (تأیید ادمین)، بیش از ۱۵٪ قرمز مسدود.

## وضعیت
وضعیت و درصد پیشرفت فقط از بخش docs/CHECKLIST.md (پایین همین فایل، بخش «وضعیت ۶ آبان ۱۴۰۵» و بخش‌های بعدی) خوانده شود؛ هر عدد دیگری قدیمی است.
HDR
echo; echo "## ۲۵ commit آخر"
sudo -u nerkhcar git log --oneline | head -n 25
echo; echo "## شاخه و وضعیت git"
sudo -u nerkhcar git branch --show-current
sudo -u nerkhcar git status --short
echo; echo "## سرویس"
systemctl is-active nerkhcar
echo; echo "## ساختار پروژه"
find . \( -path ./venv -o -path ./.git -o -path ./backups -o -path ./data -o -path ./logs -o -path ./.cache -o -path ./.ssh -o -name __pycache__ \) -prune -o -type f ! -name .env -print | sort
echo; echo "## تعداد خط فایل‌های py"
find app tools tests -name '*.py' -not -path '*/__pycache__/*' | sort | xargs wc -l
echo; echo "## docs/RULES.md"
cat docs/RULES.md
echo; echo "## docs/CHECKLIST.md"
cat docs/CHECKLIST.md
echo; echo "## migrations"
cat app/data/migrations/*.sql
echo; echo "## requirements.txt"
cat requirements.txt
echo; echo "## کد کامل app و tools"
find app tools \( -name '*.py' -o -name '*.sh' \) -not -path '*/__pycache__/*' | sort | while read -r f; do
  echo; echo "### FILE: $f"; cat "$f"
done
echo; echo "## نام فایل‌های تست"
ls tests
echo; echo "=== پایان بسته ==="
} 2>&1 | sed -E 's/AIza[0-9A-Za-z_-]{20,}/[REDACTED]/g; s/[0-9]{8,10}:[A-Za-z0-9_-]{30,}/[REDACTED]/g' > "$OUT"
chmod 600 "$OUT"
wc -lc "$OUT"
