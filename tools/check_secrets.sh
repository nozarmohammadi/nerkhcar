#!/usr/bin/env bash
# بررسی می‌کند توکن یا رازی در فایل‌های git نباشد.
cd "$(dirname "$0")/.." || exit 1
bad=0

if git ls-files --cached | grep -qE '(^|/)\.env$'; then
  echo "❌ فایل .env در git است"; bad=1
fi

if git grep -nIE '[0-9]{8,10}:[A-Za-z0-9_-]{35}' -- . ':!tools/check_secrets.sh' >/dev/null 2>&1; then
  echo "❌ چیزی شبیه توکن تلگرام پیدا شد"; bad=1
fi

if git grep -nIiE '(password|passwd|secret|api_key)[[:space:]]*=[[:space:]]*["'"'"'][^"'"'"']{4,}' -- . ':!tools/check_secrets.sh' >/dev/null 2>&1; then
  echo "❌ چیزی شبیه رمز ثابت در کد پیدا شد"; bad=1
fi

if [ -f .env ]; then
  tok=$(grep '^BOT_TOKEN=' .env | cut -d= -f2-)
  if [ -n "$tok" ] && git grep -qF -- "$tok"; then
    echo "❌ توکن واقعی در فایل‌های git است"; bad=1
  fi
fi

[ $bad -eq 0 ] && echo "✅ راز پیدا نشد"
exit $bad
