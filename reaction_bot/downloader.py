"""کلیپ منبع رو می‌گیره: یا مستقیم لینک ریل/پست اینستاگرام (با yt-dlp) یا
یه فایل ویدیوی محلی که خودت قبلاً از اینستاگرام ذخیره کردی.
"""
import os
import re

from config import config

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def is_url(source: str) -> bool:
    return bool(_URL_RE.match(source.strip()))


def fetch_source_video(source: str) -> str:
    """مسیر محلی کلیپ منبع رو برمی‌گردونه. `source` یا لینک اینستاگرامه یا
    مسیر یه فایل محلی موجود."""
    if not is_url(source):
        path = os.path.abspath(source)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"ویدیوی منبع پیدا نشد: {path}")
        return path
    return _download_from_url(source)


def _download_from_url(url: str) -> str:
    import yt_dlp

    out_template = os.path.join(config.downloads_dir, "%(id)s.%(ext)s")
    ydl_opts = {
        "outtmpl": out_template,
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
