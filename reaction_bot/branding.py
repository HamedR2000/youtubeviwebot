"""نوار سابسکرایب/لایک که قراره پایین همه‌ی کلیپ‌های نهایی بشینه -- چه
ویدیویی که از این پایپ‌لاین (composer.py) ساخته شده باشه، چه یه ویدیوی
آماده (مثلاً خروجی HeyGen) که مستقیم برای آپلود آوردیش."""
import os

from moviepy import CompositeVideoClip, ImageClip, VideoFileClip
from PIL import Image, ImageDraw

from ig_text_overlay import vazirmatn

BANNER_BG = (12, 12, 14, 215)
BANNER_TEXT = "سابسکرایب کن و لایک رو یادت نره"
BANNER_HEIGHT_RATIO = 0.07
BANNER_MIN_HEIGHT_PX = 56


def _build_banner_image(width: int, height: int, text: str) -> Image.Image:
    img = Image.new("RGBA", (width, height), BANNER_BG)
    draw = ImageDraw.Draw(img)

    font = vazirmatn(int(height * 0.5), "Bold")
    text_w = draw.textlength(text, font=font, direction="rtl", language="fa")
    bbox = draw.textbbox((0, 0), text, font=font, direction="rtl", language="fa")
    text_h = bbox[3] - bbox[1]
    x = (width - text_w) / 2
    y = (height - text_h) / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255), direction="rtl", language="fa")

    return img


def add_subscribe_banner(input_path: str, output_path: str, text: str = BANNER_TEXT) -> str:
    """یه نوار متنی همیشگی (کل مدت ویدیو) به پایین صفحه اضافه می‌کنه و
    output_path رو برمی‌گردونه. ارتفاع نوار متناسب با ارتفاع خود ویدیوعه،
    نه یه عدد ثابت -- روی هر اندازه‌ای از ویدیو (چه Shorts خودمون چه
    خروجی HeyGen) درست جا می‌افته."""
    clip = VideoFileClip(input_path)
    bar_h = max(BANNER_MIN_HEIGHT_PX, int(clip.h * BANNER_HEIGHT_RATIO))

    banner_img = _build_banner_image(clip.w, bar_h, text)
    banner_path = output_path + ".banner.png"
    banner_img.save(banner_path)
    banner_clip = ImageClip(banner_path).with_duration(clip.duration).with_position((0, clip.h - bar_h))

    video = CompositeVideoClip([clip, banner_clip])
    video.write_videofile(
        output_path,
        fps=clip.fps or 30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        logger=None,
    )

    clip.close()
    video.close()
    os.remove(banner_path)
    return output_path
