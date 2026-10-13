"""یه فریم «باحال» از خودِ ویدیو (نه کارت متنی مقدمه/پایان‌بندی) به‌عنوان
تامبنیل یوتیوب انتخاب می‌کنه -- چون publish_ready.py فایل نهایی (با
کارت‌های intro/outro از قبل پخته‌شده) رو می‌گیره، باید دقیقاً بدونیم اون
کارت‌ها چند ثانیه‌ن تا فریم رو از وسط بخش اصلی (نه از روی کارت سیاه) در
بیاریم -- همون intro_seconds/outro_seconds پیش‌فرض edit.py."""
import os

from moviepy import VideoFileClip
from PIL import Image

DEFAULT_INTRO_SECONDS = 3.0
DEFAULT_OUTRO_SECONDS = 2.5
POSITION = 0.4  # نسبت داخل بخش اصلی (نه کل ویدیو) که فریم ازش گرفته می‌شه


def extract_thumbnail(
    video_path: str,
    output_path: str,
    intro_seconds: float = DEFAULT_INTRO_SECONDS,
    outro_seconds: float = DEFAULT_OUTRO_SECONDS,
) -> str:
    with VideoFileClip(video_path) as clip:
        duration = clip.duration
        main_start = min(intro_seconds, duration * 0.3)
        main_end = max(duration - outro_seconds, main_start + 0.1)
        if main_end <= main_start:
            main_start, main_end = 0.0, duration
        t = main_start + (main_end - main_start) * POSITION
        t = min(t, duration - 0.05) if duration > 0.05 else 0.0
        frame = clip.get_frame(t)

    Image.fromarray(frame).convert("RGB").save(output_path, format="JPEG", quality=92)
    return output_path
