"""به‌جای فورک‌کردن، همون کمک‌توابع رندر متن با Pillow که برای instagram_bot
نوشته شده (چیدمان راست‌به‌چپ فارسی، بارگذاری فونت) رو دوباره export می‌کنه
-- هر دو پروژه متن رو روی فریم ویدیو/عکس به یه شکل می‌سوزونن، و پوشه‌ی
fonts/ (فایل‌های حجیم .ttf) از قبل زیر instagram_bot/ هست.

عمداً sys.path رو دستکاری نمی‌کنه (برخلاف یه نسخه‌ی قبلی این فایل) --
چون instagram_bot و reaction_bot هر دو یه ماژول config.py جدا دارن، اگه
مسیر instagram_bot جلوتر از خود reaction_bot به sys.path اضافه بشه، هر
`import config` بعدی توی کل پروسه (مثلاً توی publish_ready.py) به‌جای
config.py خودِ reaction_bot، اون یکی رو لود می‌کنه -- یه باگ واقعی که یه
بار سرمون اومد. به‌جاش فایل رو مستقیم با importlib از روی مسیرش لود
می‌کنیم، بدون اثر جانبی روی import های دیگه.
"""
import importlib.util
import os

_TEXT_OVERLAY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "instagram_bot", "text_overlay.py"
)
_spec = importlib.util.spec_from_file_location("_instagram_bot_text_overlay", _TEXT_OVERLAY_PATH)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

draw_wrapped_rtl = _module.draw_wrapped_rtl
rounded_panel = _module.rounded_panel
vazirmatn = _module.vazirmatn

__all__ = [
    "draw_wrapped_rtl",
    "rounded_panel",
    "vazirmatn",
]
