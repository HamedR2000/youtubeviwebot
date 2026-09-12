"""ترکیب نهایی: کلیپ منبع رو توی ~۶۰٪ بالای بوم ۹:۱۶ می‌ذاره و عکس آواتار
(PNG با پس‌زمینه‌ی شفاف، طراحی‌شده بیرون از این پروژه -- نگاه کن به
README.md "آواتار ری‌اکشن") رو وسط‌چین پایین می‌ذاره، با یه نوسان ملایم
بالا/پایین برای حس زنده بودن. عمداً هیچ نوشته‌ای روی صفحه نیست -- فقط
تصویر آواتار. کلیپ منبع هیچ‌وقت تمام‌صفحه نیست و بخش ری‌اکشن سهم واقعی و
دیده‌شدنی از صفحه داره (نگاه کن به README.md بخش "نکات حقوقی/ریسک").
"""
import math

from moviepy import ColorClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, VideoFileClip, afx
from PIL import Image

from config import config

BACKGROUND = (16, 16, 20)
ACCENT = (255, 72, 66)
VOICE_VOLUME = 1.0
SOURCE_AUDIO_VOLUME_WITH_VOICE = 0.15

AVATAR_MARGIN = 40
AVATAR_MAX_WIDTH_RATIO = 0.85
AVATAR_BOB_AMPLITUDE_PX = 8
AVATAR_BOB_PERIOD_S = 2.5


def _fit_and_crop(clip: VideoFileClip, width: int, height: int) -> VideoFileClip:
    scale = max(width / clip.w, height / clip.h)
    resized = clip.resized(scale)
    return resized.cropped(
        x_center=resized.w / 2, y_center=resized.h / 2, width=width, height=height
    )


def _avatar_clip(avatar_path: str, panel_h: int, panel_top: int, duration: float) -> ImageClip:
    """آواتار رو وسط پنل جا می‌ده (هم افقی هم عمودی) و یه نوسان عمودی ملایم
    بهش می‌ده. اندازه‌اش هم با ارتفاع پنل هم با یه سقف عرض محدود می‌شه تا
    اگه بعداً عکس دیگه‌ای با نسبت‌ابعاد متفاوت جایگزینش کردی، کش نیاد."""
    max_h = panel_h - 2 * AVATAR_MARGIN
    max_w = int(config.TARGET_W * AVATAR_MAX_WIDTH_RATIO)

    with Image.open(avatar_path) as img:
        img_w, img_h = img.size
    scale = min(max_h / img_h, max_w / img_w)
    disp_w, disp_h = int(img_w * scale), int(img_h * scale)

    clip = ImageClip(avatar_path).resized((disp_w, disp_h))
    x = (config.TARGET_W - disp_w) // 2
    base_y = panel_top + (panel_h - disp_h) // 2

    def position(t: float) -> tuple[float, float]:
        bob = AVATAR_BOB_AMPLITUDE_PX * math.sin(2 * math.pi * t / AVATAR_BOB_PERIOD_S)
        return (x, base_y + bob)

    return clip.with_duration(duration).with_position(position)


def compose_reaction_video(
    source_path: str,
    output_path: str,
    voice_path: str | None = None,
    avatar_path: str | None = None,
) -> str:
    """یه فایل mp4 آماده‌ی Shorts با اندازه‌ی ۱۰۸۰×۱۹۲۰ می‌سازه: کلیپ منبع
    بالا، عکس آواتار (در صورت وجود) وسط‌چین پایین -- بدون هیچ متنی روی
    صفحه. مسیر output_path رو برمی‌گردونه.

    avatar_path (اختیاری) یه PNG با پس‌زمینه‌ی شفاف از کاراکتر ری‌اکشنه --
    این پروژه خودش کاراکتر رو تولید نمی‌کنه (نگاه کن به README.md).

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
        ColorClip((config.TARGET_W, config.TARGET_H), color=BACKGROUND).with_duration(duration),
        # خط رنگی مرز، تا جدایی «کلیپ منبع» از «ری‌اکشن» واضح باشه.
        ColorClip((config.TARGET_W, 6), color=ACCENT).with_duration(duration).with_position((0, source_h)),
        fitted,
    ]

    if avatar_path:
        layers.append(_avatar_clip(avatar_path, panel_h, source_h, duration))

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
    return output_path
