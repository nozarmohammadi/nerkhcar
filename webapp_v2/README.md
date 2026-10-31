# README: ساختار مینی‌اپ نرخ‌کار (الف + نوار ارز/طلا + لینک مستقیم)

## قانون طلایی تغییر
| می‌خواهم عوض کنم | فقط این فایل |
|---|---|
| رنگ، فاصله، گردی گوشه، فونت، اندازهٔ آیکون | css/tokens.css |
| هر متن فارسی | js/texts.js |
| هر آیکون | js/icons.js |
| ظاهر یک کلاس | css/components.css |
| یک صفحه | js/pages/NAME.js |

## رنگ‌ها (tokens.css)
--c-bg پس‌زمینه | --c-surface کارت و نوار | --c-text متن | --c-muted خاکستری | --c-line خط | --c-primary سبز اصلی | --c-on-primary متن روی سبز | --c-accent طلایی | --c-danger قرمز.
حالت تاریک: همان نام‌ها، مقدار دیگر. فاصله --s-1..5 | گردی --r-1, --r-2, --r-pill | فونت --f-xs..xxl | آیکون --icon-size, --icon-stroke.

## آیکون‌ها (icons.js)
prices, compare, estimate, my, more (خطی ۲۴×۲۴). آیکون جدید: یک خط path در icons.js، خواندن با NK.U.icon('name').

## کلاس‌ها (l- چیدمان، c- کامپوننت)
- چیدمان: l-app، l-page
- متن: c-title، c-note، c-label، c-link
- فرم: c-input، c-form، c-btn، c-btn--ghost
- چیپ: c-chips، c-chip، c-chip--on
- قیمت: c-price، c-price__num، c-price__unit، c-price--big
- ردیف: c-row، c-row__main، c-row__name، c-row__sub، c-row--dim
- کارت: c-fx، c-fx__item، c-fx__value، c-result
- جدول: c-scroll، c-table
- حالت‌ها: c-empty، c-skeleton
- منوی پایین: c-tabbar، c-tab، c-tab--on
- آیکون: c-icon

## لینک مستقیم (startapp)
car_ID | cmp_ID_ID | est ؛ منبع بعد از دو زیرخط: ch, ig, bot, web. مثال: car_123__ch.
فعلاً id = trim_id اگر API بدهد، وگرنه شمارهٔ ردیف (موقت).

## هنوز نیست (عمداً، بدون دادهٔ ساختگی)
نمودار و تغییر روزانه، ارز/سکه/طلا، ذخیرهٔ دائمی و هشدار، /api/estimate.
