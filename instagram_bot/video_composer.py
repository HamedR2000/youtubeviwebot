"""Compose the final Reel: crop the stock clip to 1080x1920, burn in a text
overlay (hook + tip + branding) rendered with Pillow, and mix in a random
royalty-free background track from music/.

Text is rendered to a transparent PNG with Pillow (not moviepy's
TextClip) specifically to avoid an ImageMagick dependency in CI.
"""
import glob
import os
import random
import textwrap

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    afx,
)

TARGET_W, TARGET_H = 1080, 1920
CLIP_DURATION_S = 15
MUSIC_VOLUME = 0.35

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _draw_wrapped(draw, text, font, box_left, box_top, box_width, fill, line_spacing=12, max_width_chars=26):
    lines = textwrap.wrap(text, width=max_width_chars)
    y = box_top
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_h = bbox[3] - bbox[1]
        draw.text((box_left, y), line, font=font, fill=fill)
        y += line_h + line_spacing
    return y


def _rounded_panel(draw, xy, fill, radius=28):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def build_text_overlay(hook: str, tip: str, brand_handle: str) -> Image.Image:
    img = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    hook_font = _load_font(64)
    tip_font = _load_font(40)
    brand_font = _load_font(36)

    margin = 64

    # Hook panel near the top third (safe from IG's own UI at the very top).
    _rounded_panel(draw, [margin, 260, TARGET_W - margin, 520], (0, 0, 0, 150))
    _draw_wrapped(draw, hook, hook_font, margin + 32, 300, TARGET_W - 2 * margin - 64,
                  fill=(255, 215, 0, 255), max_width_chars=22)

    # Tip panel in the lower third (safe from IG's caption/like-bar UI).
    _rounded_panel(draw, [margin, 1360, TARGET_W - margin, 1650], (0, 0, 0, 150))
    _draw_wrapped(draw, tip, tip_font, margin + 32, 1400, TARGET_W - 2 * margin - 64,
                  fill=(255, 255, 255, 255), max_width_chars=34)

    # Branding line, bottom-most.
    draw.text((margin, 1700), brand_handle, font=brand_font, fill=(255, 215, 0, 255))

    return img


def _fit_and_crop(clip: VideoFileClip) -> VideoFileClip:
    scale = max(TARGET_W / clip.w, TARGET_H / clip.h)
    resized = clip.resize(scale)
    x_center, y_center = resized.w / 2, resized.h / 2
    return resized.crop(
        x_center=x_center, y_center=y_center, width=TARGET_W, height=TARGET_H
    )


def _pick_music_track(music_dir: str) -> str:
    tracks = glob.glob(os.path.join(music_dir, "*.mp3")) + glob.glob(os.path.join(music_dir, "*.m4a"))
    if not tracks:
        raise FileNotFoundError(
            f"No .mp3/.m4a files found in {music_dir}. Add royalty-free tracks there "
            "(see instagram_bot/README.md -> 'Background music')."
        )
    return random.choice(tracks)


def compose_video(raw_video_path: str, hook: str, tip: str, brand_handle: str,
                   music_dir: str, output_path: str) -> None:
    base = VideoFileClip(raw_video_path).without_audio()
    duration = min(CLIP_DURATION_S, base.duration)
    base = _fit_and_crop(base).subclip(0, duration)

    overlay_img = build_text_overlay(hook, tip, brand_handle)
    overlay_path = output_path + ".overlay.png"
    overlay_img.save(overlay_path)
    overlay_clip = ImageClip(overlay_path).set_duration(duration)

    video = CompositeVideoClip([base, overlay_clip])

    track_path = _pick_music_track(music_dir)
    music = AudioFileClip(track_path)
    if music.duration < duration:
        music = afx.audio_loop(music, duration=duration)
    else:
        music = music.subclip(0, duration)
    music = music.volumex(MUSIC_VOLUME).audio_fadein(1).audio_fadeout(1.5)

    video = video.set_audio(CompositeAudioClip([music]))

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
    music.close()
    os.remove(overlay_path)
