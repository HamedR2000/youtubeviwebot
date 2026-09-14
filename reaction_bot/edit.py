"""ابزارهای تدوین سبک -- مقدمه/پایان‌بندی متنی و زوم بصری روی یه بخش
خاص. زیرنویس/کامنتِ مبتنی بر حرفِ داخل ویدیو اینجا نیست، چون تبدیل
گفتار-به-متن توی این محیط در دسترس نیست (مدل‌هاش مسدودن) -- نگاه کن به
README.md.
"""
import os

from moviepy import ColorClip, CompositeVideoClip, ImageClip, VideoFileClip, concatenate_videoclips
from PIL import Image, ImageDraw

from config import config
from ig_text_overlay import draw_wrapped_rtl, vazirmatn

CARD_BG = (18, 18, 22)


def _text_card(text: str, duration: float, width: int, height: int) -> ImageClip:
    """کارت رو دقیقاً هم‌اندازه‌ی خودِ ویدیوی مقصد می‌سازه -- وگرنه موقع
    اتصال (concatenate) چون اندازه‌ها یکی نیست، moviepy دور فریم کوچیک‌تر
    حاشیه‌ی سیاه می‌ذاره (letterbox)."""
    img = Image.new("RGB", (width, height), CARD_BG)
    draw = ImageDraw.Draw(img)
    font_size = max(28, int(height * 0.033))
    font = vazirmatn(font_size, "Bold")
    margin = int(width * 0.07)
    draw_wrapped_rtl(
        draw, text, font, width - margin, height // 2 - int(font_size * 2.3),
        width - 2 * margin, fill=(255, 255, 255, 255), line_spacing=16,
    )
    path = os.path.join(config.outputs_dir, f"_card_{abs(hash(text))}.png")
    img.save(path)
    clip = ImageClip(path).with_duration(duration)
    clip._card_tmp_path = path  # برای پاک‌کردن بعد از رندر نهایی
    return clip


def _punch_in_zoom(clip: VideoFileClip, start: float, end: float, max_zoom: float = 1.15) -> VideoFileClip:
    """یه زوم ملایم و پیوسته روی بازه‌ی [start, end] -- قبل و بعدش همون
    اندازه‌ی عادیه، وسط بازه به‌آرومی بزرگ‌نمایی می‌شه و برمی‌گرده."""
    w, h = clip.w, clip.h

    def scale_at(t: float) -> float:
        if t < start or t > end:
            return 1.0
        mid = (start + end) / 2
        span = (end - start) / 2 or 1e-6
        # مثلث: از ۱ می‌ره به max_zoom وسط بازه، برمی‌گرده به ۱
        progress = 1 - abs(t - mid) / span
        return 1.0 + (max_zoom - 1.0) * max(0.0, progress)

    def make_frame(get_frame, t):
        import numpy as np
        from PIL import Image as PILImage

        frame = get_frame(t)
        s = scale_at(t)
        if s <= 1.001:
            return frame
        img = PILImage.fromarray(frame)
        new_w, new_h = int(w * s), int(h * s)
        img = img.resize((new_w, new_h), PILImage.LANCZOS)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        img = img.crop((left, top, left + w, top + h))
        return np.array(img)

    return clip.transform(make_frame)


def add_intro_outro(
    video_path: str,
    output_path: str,
    intro_text: str | None = None,
    outro_text: str | None = "نظر شما چیه؟",
    intro_seconds: float = 3.0,
    outro_seconds: float = 2.5,
    zoom_at: tuple[float, float] | None = None,
) -> str:
    """قبل و بعد ویدیو یه کارت متنی اضافه می‌کنه، و اگه zoom_at داده بشه
    (start, end) یه زوم ملایم روی اون بازه از ویدیوی اصلی می‌ذاره."""
    main = VideoFileClip(video_path)
    if zoom_at:
        main = _punch_in_zoom(main, zoom_at[0], zoom_at[1])

    clips = [main]
    card_paths = []

    if intro_text:
        intro = _text_card(intro_text, intro_seconds, main.w, main.h)
        card_paths.append(intro._card_tmp_path)
        clips.insert(0, intro)

    if outro_text:
        outro = _text_card(outro_text, outro_seconds, main.w, main.h)
        card_paths.append(outro._card_tmp_path)
        clips.append(outro)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        output_path, fps=30, codec="libx264", audio_codec="aac",
        threads=4, preset="medium", logger=None,
    )

    main.close()
    final.close()
    for p in card_paths:
        os.remove(p)
    return output_path
