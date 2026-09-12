"""ترکیب نهایی فاز ۱: هنوز آواتار نداره (فاز ۲). کلیپ منبع رو توی ~۶۰٪ بالای
بوم ۹:۱۶ می‌ذاره و متن اسکریپت ری‌اکشن رو روی پنل پایین می‌سوزونه -- یعنی
کلیپ منبع هیچ‌وقت تمام‌صفحه نیست و بخش ری‌اکشن سهم واقعی و دیده‌شدنی از
صفحه داره (نگاه کن به README.md بخش "نکات حقوقی/ریسک").
"""
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


def _fit_and_crop(clip: VideoFileClip, width: int, height: int) -> VideoFileClip:
    scale = max(width / clip.w, height / clip.h)
    resized = clip.resized(scale)
    return resized.cropped(
        x_center=resized.w / 2, y_center=resized.h / 2, width=width, height=height
    )


def _build_caption_panel(script_text: str, panel_w: int, panel_h: int) -> Image.Image:
    img = Image.new("RGBA", (panel_w, panel_h), PANEL_BG)
    draw = ImageDraw.Draw(img)

    # خط رنگی مرز، تا جدایی «کلیپ منبع» از «ری‌اکشن» واضح باشه.
    draw.rectangle([0, 0, panel_w, 6], fill=ACCENT)

    badge_font = vazirmatn(32, "Bold")
    margin = 56
    rounded_panel(draw, [margin, 40, margin + 220, 96], (255, 72, 66, 220), radius=20)
    draw.text((margin + 24, 50), BADGE_TEXT, font=badge_font, fill=(255, 255, 255, 255))

    text_top = 140
    max_width = panel_w - 2 * margin
    script_font = vazirmatn(52, "Bold")
    draw_wrapped_rtl(
        draw, script_text, script_font, panel_w - margin, text_top, max_width,
        fill=(255, 255, 255, 255), line_spacing=14,
    )

    return img


def compose_reaction_video(
    source_path: str,
    script_text: str,
    output_path: str,
    voice_path: str | None = None,
) -> str:
    """یه فایل mp4 آماده‌ی Shorts با اندازه‌ی ۱۰۸۰×۱۹۲۰ می‌سازه: کلیپ منبع
    بالا، پنل کپشن ری‌اکشن پایین. مسیر output_path رو برمی‌گردونه.

    voice_path (اختیاری) یه فایل صوتی ری‌اکشن (ضبط‌شده یا خروجی TTS) هست که
    روی صدای منبع (با صدای کم‌شده) میکس می‌شه -- چون هنوز منبع صدا مشخص
    نشده (چک‌لیست README.md)، فعلاً اختیاریه.
    """
    source_h = int(config.TARGET_H * config.SOURCE_HEIGHT_RATIO)
    panel_h = config.TARGET_H - source_h

    base = VideoFileClip(source_path)
    duration = min(config.MAX_CLIP_SECONDS, base.duration)
    base = base.subclipped(0, duration)
    fitted = _fit_and_crop(base, config.TARGET_W, source_h).with_position((0, 0))

    panel_img = _build_caption_panel(script_text, config.TARGET_W, panel_h)
    panel_path = output_path + ".panel.png"
    panel_img.save(panel_path)
    panel_clip = ImageClip(panel_path).with_duration(duration).with_position((0, source_h))

    background = ColorClip((config.TARGET_W, config.TARGET_H), color=(16, 16, 20)).with_duration(duration)
    video = CompositeVideoClip([background, fitted, panel_clip])

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
