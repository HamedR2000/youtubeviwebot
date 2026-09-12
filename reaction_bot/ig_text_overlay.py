"""به‌جای فورک‌کردن، همون کمک‌توابع رندر متن با Pillow که برای instagram_bot
نوشته شده (چیدمان راست‌به‌چپ فارسی، بارگذاری فونت) رو دوباره export می‌کنه
-- هر دو پروژه متن رو روی فریم ویدیو/عکس به یه شکل می‌سوزونن، و پوشه‌ی
fonts/ (فایل‌های حجیم .ttf) از قبل زیر instagram_bot/ هست.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "instagram_bot"))

from text_overlay import (  # noqa: E402  (import باید بعد از تنظیم sys.path باشه)
    draw_wrapped_rtl,
    rounded_panel,
    vazirmatn,
)

__all__ = [
    "draw_wrapped_rtl",
    "rounded_panel",
    "vazirmatn",
]
