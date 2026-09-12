"""Compose the final Reel: crop the stock clip to 1080x1920, burn in a text
overlay (hook + tip + branding) rendered with Pillow, and mix in a random
royalty-free background track from music/.

Text is rendered to a transparent PNG with Pillow (not moviepy's
TextClip) specifically to avoid an ImageMagick dependency in CI.
"""
import glob
import os
import random

from PIL import Image, ImageDraw
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    afx,
)

from text_overlay import draw_wrapped, draw_wrapped_rtl, load_font, rounded_panel, vazirmatn

TARGET_W, TARGET_H = 1080, 1920
CLIP_DURATION_S = 15
MUSIC_VOLUME = 0.35


def build_text_overlay(hook: str, tip: str, brand_handle: str, rtl: bool = False) -> Image.Image:
    """rtl=True renders hook/tip with the Persian/Arabic-script font, shaped
    and right-aligned within each panel -- used on Persian-language days
    (see ENGLISH_WEEKDAYS in main.py). brand_handle stays Latin/LTR either
    way, same as the image cards."""
    img = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    brand_font = load_font(36)
    margin = 64

    # Hook panel near the top third (safe from IG's own UI at the very top).
    rounded_panel(draw, [margin, 260, TARGET_W - margin, 520], (0, 0, 0, 150))
    # Tip panel in the lower third (safe from IG's caption/like-bar UI).
    rounded_panel(draw, [margin, 1360, TARGET_W - margin, 1650], (0, 0, 0, 150))

    if rtl:
        hook_font = vazirmatn(56, "Bold")
        tip_font = vazirmatn(36, "Regular")
        right_x = TARGET_W - margin - 32
        draw_wrapped_rtl(draw, hook, hook_font, right_x, 300, TARGET_W - 2 * margin - 64,
                          fill=(255, 215, 0, 255))
        draw_wrapped_rtl(draw, tip, tip_font, right_x, 1400, TARGET_W - 2 * margin - 64,
                          fill=(255, 255, 255, 255))
    else:
        hook_font = load_font(64)
        tip_font = load_font(40)
        draw_wrapped(draw, hook, hook_font, margin + 32, 300,
                     fill=(255, 215, 0, 255), max_width_chars=22)
        draw_wrapped(draw, tip, tip_font, margin + 32, 1400,
                     fill=(255, 255, 255, 255), max_width_chars=34)

    # Branding line, bottom-most.
    draw.text((margin, 1700), brand_handle, font=brand_font, fill=(255, 215, 0, 255))

    return img


def _fit_and_crop(clip: VideoFileClip) -> VideoFileClip:
    scale = max(TARGET_W / clip.w, TARGET_H / clip.h)
    resized = clip.resized(scale)
    x_center, y_center = resized.w / 2, resized.h / 2
    return resized.cropped(
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
                   music_dir: str, output_path: str, rtl: bool = False) -> None:
    base = VideoFileClip(raw_video_path).without_audio()
    duration = min(CLIP_DURATION_S, base.duration)
    base = _fit_and_crop(base).subclipped(0, duration)

    overlay_img = build_text_overlay(hook, tip, brand_handle, rtl=rtl)
    overlay_path = output_path + ".overlay.png"
    overlay_img.save(overlay_path)
    overlay_clip = ImageClip(overlay_path).with_duration(duration)

    video = CompositeVideoClip([base, overlay_clip])

    track_path = _pick_music_track(music_dir)
    music = AudioFileClip(track_path)
    if music.duration < duration:
        music = music.with_effects([afx.AudioLoop(duration=duration)])
    else:
        music = music.subclipped(0, duration)
    music = music.with_effects([
        afx.MultiplyVolume(MUSIC_VOLUME),
        afx.AudioFadeIn(1),
        afx.AudioFadeOut(1.5),
    ])

    video = video.with_audio(CompositeAudioClip([music]))

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
