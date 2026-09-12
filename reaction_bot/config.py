"""تنظیمات مبتنی بر متغیر محیطی برای پایپ‌لاین ری‌اکشن. هم‌الگو با
instagram_bot/config.py: سکرت‌ها/مسیرها از env vars (یا یه فایل .env
محلی) میان تا همون کد روی لپ‌تاپ یا VPS بدون تغییر اجرا بشه.
"""
import os


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


class Config:
    # جایی که کلیپ‌های دانلودشده، خروجی‌های ترکیب‌شده و وضعیت OAuth ذخیره می‌شن.
    WORK_DIR = _env("REACTION_WORK_DIR", os.path.join(os.path.dirname(__file__), "workdir"))

    @property
    def downloads_dir(self) -> str:
        path = os.path.join(self.WORK_DIR, "downloads")
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def outputs_dir(self) -> str:
        path = os.path.join(self.WORK_DIR, "outputs")
        os.makedirs(path, exist_ok=True)
        return path

    # OAuth یوتیوب (YouTube Data API v3، فلوی Installed App). هر دو رو توی
    # Google Cloud Console بساز -- نگاه کن به reaction_bot/README.md بخش
    # "راه‌اندازی یوتیوب".
    YOUTUBE_CLIENT_SECRETS_FILE = _env(
        "YOUTUBE_CLIENT_SECRETS_FILE", os.path.join(os.path.dirname(__file__), "client_secret.json")
    )
    YOUTUBE_TOKEN_FILE = _env(
        "YOUTUBE_TOKEN_FILE", os.path.join(os.path.dirname(__file__), "token.json")
    )
    YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    # پیش‌فرض "private": آپلود یه Short یه اقدام عمومی و سخت‌برگشته، پس
    # پایپ‌لاین هیچ‌وقت به‌صورت پیش‌فرض مستقیم "public" منتشر نمی‌کنه --
    # برای تغییرش در هر اجرا صریحاً --privacy بده.
    DEFAULT_PRIVACY_STATUS = _env("YOUTUBE_DEFAULT_PRIVACY", "private")
    DEFAULT_CATEGORY_ID = _env("YOUTUBE_DEFAULT_CATEGORY_ID", "23")  # "طنز/کمدی"

    # بوم خروجی: عمودی ۹:۱۶ برای Shorts.
    TARGET_W = 1080
    TARGET_H = 1920
    # کلیپ منبع فقط بخش بالای فریم رو پر می‌کنه (نه تمام صفحه) و پنل
    # "ری‌اکشن" پایینی برای تفسیر/کپشن (و در فاز ۲، آواتار) کنار گذاشته
    # شده -- نگاه کن به README.md بخش "نکات حقوقی/ریسک".
    SOURCE_HEIGHT_RATIO = float(_env("REACTION_SOURCE_HEIGHT_RATIO", "0.6"))
    MAX_CLIP_SECONDS = float(_env("REACTION_MAX_CLIP_SECONDS", "58"))


config = Config()
