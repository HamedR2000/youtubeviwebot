"""ترکیب نهایی: کلیپ منبع رو توی ~۶۰٪ بالای بوم ۹:۱۶ می‌ذاره و پنل ری‌اکشن
رو زیرش می‌سازه -- متن اسکریپت، و در صورت وجود عکس آواتار (PNG با
پس‌زمینه‌ی شفاف، طراحی‌شده بیرون از این پروژه -- نگاه کن به README.md
"آواتار ری‌اکشن") با یه حرکت ملایم بالا/پایین برای حس زنده بودن، چون فعلاً
صدایی برای لب‌سینک نداریم. کلیپ منبع هیچ‌وقت تمام‌صفحه نیست و بخش ری‌اکشن
سهم واقعی و دیده‌شدنی از صفحه داره (نگاه کن به README.md بخش "نکات
حقوقی/ریسک").
"""
import math
import os

from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    afx,
)
from PIL import Image, ImageDraw

from config import config
from ig_text_overlay import draw_wrapped_rtl, rounded_panel, vazirmatn

PANEL_BG = (16, 16, 20, 255)
ACCENT = (255, 72, 66, 255)
BADGE_TEXT = "ری‌اکشن"
VOICE_VOLUME = 1.0
SOURCE_AUDIO_VOLUME_WITH_VOICE = 0.15

AVATAR_MARGIN = 40
AVATAR_MAX_WIDTH_RATIO = 0.42
AVATAR_BOB_AMPLITUDE_PX = 8
AVATAR_BOB_PERIOD_S = 2.5


def _fit_and_crop(clip: VideoFileClip, width: int, height: int) -> VideoFileClip:
    scale = max(width / clip.w, height / clip.h)
    resized = clip.resized(scale)
    return resized.cropped(
        x_center=resized.w / 2, y_center=resized.h / 2, width=width, height=height
    )


def _build_caption_panel(script_text: str, panel_w: int, panel_h: int, text_left: int) -> Image.Image:
    img = Image.new("RGBA", (panel_w, panel_h), PANEL_BG)
    draw = ImageDraw.Draw(img)

    # خط رنگی مرز، تا جدایی «کلیپ منبع» از «ری‌اکشن» واضح باشه.
    draw.rectangle([0, 0, panel_w, 6], fill=ACCENT)

    margin = 56
    right_x = panel_w - margin

    badge_font = vazirmatn(32, "Bold")
    badge_w = draw.textlength(BADGE_TEXT, font=badge_font, direction="rtl", language="fa") + 48
    badge_left = right_x - badge_w
    rounded_panel(draw, [badge_left, 40, right_x, 96], (255, 72, 66, 220), radius=20)
    draw.text((badge_left + 24, 50), BADGE_TEXT, font=badge_font, fill=(255, 255, 255, 255))

    text_top = 140
    max_width = right_x - text_left
    script_font = vazirmatn(52, "Bold")
    draw_wrapped_rtl(
        draw, script_text, script_font, right_x, text_top, max_width,
        fill=(255, 255, 255, 255), line_spacing=14,
    )

    return img


def _avatar_clip(avatar_path: str, panel_h: int, panel_top: int, duration: float) -> tuple[ImageClip, int]:
    """آواتار رو گوشه‌ی چپ پنل جا می‌ده و یه نوسان عمودی ملایم بهش می‌ده.
    اندازه‌اش هم با ارتفاع پنل هم با یه سقف عرض محدود می‌شه (وگرنه یه عکس
    پهن -- مثلاً با ویلچر کنارش -- کل جای متن رو می‌گیره)، و عمودی وسط‌چین
    می‌شه. عرض رزروشده رو هم برمی‌گردونه تا متن کپشن زیرش نره."""
    max_h = panel_h - 2 * AVATAR_MARGIN
    max_w = int(config.TARGET_W * AVATAR_MAX_WIDTH_RATIO)

    with Image.open(avatar_path) as img:
        img_w, img_h = img.size
    scale = min(max_h / img_h, max_w / img_w)
    disp_w, disp_h = int(img_w * scale), int(img_h * scale)

    clip = ImageClip(avatar_path).resized((disp_w, disp_h))
    x = AVATAR_MARGIN
    base_y = panel_top + (panel_h - disp_h) // 2

    def position(t: float) -> tuple[float, float]:
        bob = AVATAR_BOB_AMPLITUDE_PX * math.sin(2 * math.pi * t / AVATAR_BOB_PERIOD_S)
        return (x, base_y + bob)

    clip = clip.with_duration(duration).with_position(position)
    reserved_width = disp_w + 2 * AVATAR_MARGIN
    return clip, reserved_width


def compose_reaction_video(
    source_path: str,
    script_text: str,
    output_path: str,
    voice_path: str | None = None,
    avatar_path: str | None = None,
) -> str:
    """یه فایل mp4 آماده‌ی Shorts با اندازه‌ی ۱۰۸۰×۱۹۲۰ می‌سازه: کلیپ منبع
    بالا، پنل کپشن ری‌اکشن (+ آواتار در صورت وجود) پایین. مسیر output_path
    رو برمی‌گردونه.

    avatar_path (اختیاری) یه PNG با پس‌زمینه‌ی شفاف از کاراکتر ری‌اکشنه --
    این پروژه خودش کاراکتر رو تولید نمی‌کنه (نگاه کن به README.md)، فقط
    عکس آماده رو کنار متن می‌ذاره و کمی نوسان بهش می‌ده.

    voice_path (اختیاری) یه فایل صوتی ری‌اکشن (ضبط‌شده یا خروجی TTS) هست که
    روی صدای منبع (با صدای کم‌شده) میکس می‌شه -- چون فعلاً بدون صداست،
    اختیاریه و به آواتار سینک نمی‌شه.
    """
    source_h = int(config.TARGET_H * config.SOURCE_HEIGHT_RATIO)
    panel_h = config.TARGET_H - source_h

    base = VideoFileClip(source_path)
    duration = min(config.MAX_CLIP_SECONDS, base.duration)
    base = base.subclipped(0, duration)
    fitted = _fit_and_crop(base, config.TARGET_W, source_h).with_position((0, 0))

    layers = [
        ColorClip((config.TARGET_W, config.TARGET_H), color=(16, 16, 20)).with_duration(duration),
        fitted,
    ]

    text_left = 56
    avatar_layer = None
    if avatar_path:
        avatar_layer, reserved_width = _avatar_clip(avatar_path, panel_h, source_h, duration)
        text_left = reserved_width

    panel_img = _build_caption_panel(script_text, config.TARGET_W, panel_h, text_left)
    panel_path = output_path + ".panel.png"
    panel_img.save(panel_path)
    panel_clip = ImageClip(panel_path).with_duration(duration).with_position((0, source_h))
    layers.append(panel_clip)

    if avatar_layer is not None:
        layers.append(avatar_layer)

    video = CompositeVideoClip(layers)

    source_audio = base.audio
    if voice_path:
        voice = AudioFileClip(voice_path)
        if voice.duration < duration:
            voice = voice.with_effects([afx.AudioLoop(duration=duration)])
        else:
            voice = voice.subclipped(0, duration)
        voice = voice.with_effects([afx.MultiplyVolume(VOICE_VOLUME)])
        tracks = [voice]
        if source_audio is not None:
            tracks.append(source_audio.with_effects([afx.MultiplyVolume(SOURCE_AUDIO_VOLUME_WITH_VOICE)]))
        video = video.with_audio(CompositeAudioClip(tracks))
    elif source_audio is not None:
        video = video.with_audio(source_audio)

    video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        logger=None,
    )

    base.close()
    video.close()
    os.remove(panel_path)
    return output_path
