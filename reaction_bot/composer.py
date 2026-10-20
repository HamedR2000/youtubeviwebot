"""ترکیب نهایی: ویدیوی منبع تمام‌صفحه (کراپ‌شده به ۹:۱۶)، عکس آواتار
(PNG با پس‌زمینه‌ی شفاف -- نگاه کن به README.md "آواتار ری‌اکشن") به‌صورت
کراپ‌شده و بزرگ، پایین صفحه و روی خودِ ویدیو، با یه نوسان ملایم برای حس
زنده بودن؛ و متن «خنده با نیما» بالای صفحه با یه نوار نیمه‌شفاف پشتش
برای خوانا موندن روی هر پس‌زمینه‌ای."""
import math
import os

from moviepy import AudioFileClip, CompositeAudioClip, CompositeVideoClip, ImageClip, VideoFileClip, afx
from PIL import Image, ImageDraw

from config import config
from ig_text_overlay import vazirmatn

VOICE_VOLUME = 1.0
SOURCE_AUDIO_VOLUME_WITH_VOICE = 0.15

AVATAR_WIDTH_RATIO = 0.62
AVATAR_BOTTOM_MARGIN = 150  # جا برای نوار سابسکرایب (branding.py) که بعداً زیرش اضافه می‌شه
AVATAR_BOB_AMPLITUDE_PX = 8
AVATAR_BOB_PERIOD_S = 2.5

CHANNEL_NAME = "خنده با نیما"
CHANNEL_NAME_COLOR = (255, 255, 255, 255)
CHANNEL_BAR_BG = (0, 0, 0, 150)
CHANNEL_BAR_TOP_MARGIN = 50
CHANNEL_BAR_HEIGHT = 110


def _fit_and_crop(clip: VideoFileClip, width: int, height: int) -> VideoFileClip:
    scale = max(width / clip.w, height / clip.h)
    resized = clip.resized(scale)
    return resized.cropped(
        x_center=resized.w / 2, y_center=resized.h / 2, width=width, height=height
    )


def _avatar_clip(avatar_path: str, duration: float) -> ImageClip:
    """آواتار رو کراپ‌شده (بدون حاشیه‌ی شفاف اضافه) و بزرگ، پایین صفحه و
    وسط‌چین روی خودِ ویدیو می‌ذاره."""
    with Image.open(avatar_path) as img:
        bbox = img.getbbox()
        img_w, img_h = (bbox[2] - bbox[0], bbox[3] - bbox[1]) if bbox else img.size

    disp_w = int(config.TARGET_W * AVATAR_WIDTH_RATIO)
    disp_h = int(disp_w * img_h / img_w)

    clip = ImageClip(avatar_path).cropped(x1=bbox[0], y1=bbox[1], x2=bbox[2], y2=bbox[3]).resized((disp_w, disp_h))
    x = (config.TARGET_W - disp_w) // 2
    base_y = config.TARGET_H - disp_h - AVATAR_BOTTOM_MARGIN

    def position(t: float) -> tuple[float, float]:
        bob = AVATAR_BOB_AMPLITUDE_PX * math.sin(2 * math.pi * t / AVATAR_BOB_PERIOD_S)
        return (x, base_y + bob)

    return clip.with_duration(duration).with_position(position)


def _channel_name_clip(duration: float) -> ImageClip:
    """متن «خنده با نیما» با یه نوار نیمه‌شفاف پشتش، بالای صفحه."""
    img = Image.new("RGBA", (config.TARGET_W, CHANNEL_BAR_HEIGHT), CHANNEL_BAR_BG)
    draw = ImageDraw.Draw(img)
    font = vazirmatn(56, "Bold")
    bbox = draw.textbbox((0, 0), CHANNEL_NAME, font=font, direction="rtl", language="fa")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (config.TARGET_W - text_w) / 2
    y = (CHANNEL_BAR_HEIGHT - text_h) / 2 - bbox[1]
    draw.text((x, y), CHANNEL_NAME, font=font, fill=CHANNEL_NAME_COLOR, direction="rtl", language="fa")

    path = os.path.join(config.outputs_dir, "_channel_name.png")
    img.save(path)
    clip = ImageClip(path).with_duration(duration).with_position((0, CHANNEL_BAR_TOP_MARGIN))
    clip._tmp_path = path
    return clip


def compose_reaction_video(
    source_path: str,
    output_path: str,
    voice_path: str | None = None,
    avatar_path: str | None = None,
) -> str:
    """یه فایل mp4 آماده‌ی Shorts با اندازه‌ی ۱۰۸۰×۱۹۲۰ می‌سازه: ویدیوی
    منبع تمام‌صفحه، آواتار (در صورت وجود) پایین صفحه روی خودِ ویدیو، و
    متن «خنده با نیما» بالای صفحه. مسیر output_path رو برمی‌گردونه.

    avatar_path (اختیاری) یه PNG با پس‌زمینه‌ی شفاف از کاراکتر ری‌اکشنه --
    این پروژه خودش کاراکتر رو تولید نمی‌کنه (نگاه کن به README.md).

    voice_path (اختیاری) یه فایل صوتی ری‌اکشن (ضبط‌شده یا خروجی TTS) هست که
    روی صدای منبع (با صدای کم‌شده) میکس می‌شه -- چون فعلاً بدون صداست،
    اختیاریه و به آواتار سینک نمی‌شه.
    """
    base = VideoFileClip(source_path)
    duration = min(config.MAX_CLIP_SECONDS, base.duration)
    base = base.subclipped(0, duration)
    fitted = _fit_and_crop(base, config.TARGET_W, config.TARGET_H).with_position((0, 0))

    layers = [fitted]

    tmp_paths = []
    if avatar_path:
        layers.append(_avatar_clip(avatar_path, duration))
    name_clip = _channel_name_clip(duration)
    layers.append(name_clip)
    tmp_paths.append(name_clip._tmp_path)

    video = CompositeVideoClip(layers, size=(config.TARGET_W, config.TARGET_H))

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
    for p in tmp_paths:
        os.remove(p)
    return output_path
