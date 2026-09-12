"""Phase-1 compositing: no avatar yet (that's phase 2). Lays the source clip
into the top ~60% of a 9:16 canvas and burns the reaction script into a
caption panel underneath -- so the source video is never full-screen and the
reaction commentary has real, visible screen time of its own (see README.md
"نکات حقوقی/ریسک").
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
from ig_text_overlay import draw_wrapped_px, draw_wrapped_rtl, load_font, rounded_panel, vazirmatn

PANEL_BG = (16, 16, 20, 255)
ACCENT = (255, 72, 66, 255)
VOICE_VOLUME = 1.0
SOURCE_AUDIO_VOLUME_WITH_VOICE = 0.15


def _fit_and_crop(clip: VideoFileClip, width: int, height: int) -> VideoFileClip:
    scale = max(width / clip.w, height / clip.h)
    resized = clip.resized(scale)
    return resized.cropped(
        x_center=resized.w / 2, y_center=resized.h / 2, width=width, height=height
    )


def _build_caption_panel(script_text: str, panel_w: int, panel_h: int, rtl: bool) -> Image.Image:
    img = Image.new("RGBA", (panel_w, panel_h), PANEL_BG)
    draw = ImageDraw.Draw(img)

    # Accent seam so the split between "source clip" and "reaction" is obvious.
    draw.rectangle([0, 0, panel_w, 6], fill=ACCENT)

    badge_font = load_font(30) if not rtl else vazirmatn(32, "Bold")
    badge_text = "ریاکشن" if rtl else "REACTION"  # "ریاکشن"
    margin = 56
    rounded_panel(draw, [margin, 40, margin + 220, 96], (255, 72, 66, 220), radius=20)
    draw.text((margin + 24, 50), badge_text, font=badge_font, fill=(255, 255, 255, 255))

    text_top = 140
    max_width = panel_w - 2 * margin
    if rtl:
        script_font = vazirmatn(52, "Bold")
        draw_wrapped_rtl(
            draw, script_text, script_font, panel_w - margin, text_top, max_width,
            fill=(255, 255, 255, 255), line_spacing=14,
        )
    else:
        script_font = load_font(48)
        draw_wrapped_px(
            draw, script_text, script_font, margin, text_top, max_width,
            fill=(255, 255, 255, 255), line_spacing=14,
        )

    return img


def compose_reaction_video(
    source_path: str,
    script_text: str,
    output_path: str,
    rtl: bool = True,
    voice_path: str | None = None,
) -> str:
    """Build a 1080x1920 Shorts-ready mp4: source clip on top, reaction
    caption panel on the bottom. Returns output_path.

    voice_path, if given, is a recorded/TTS reaction voiceover mixed over the
    (ducked) source audio -- optional in phase 1 since the project hasn't
    settled on a voice source yet (see README.md checklist).
    """
    source_h = int(config.TARGET_H * config.SOURCE_HEIGHT_RATIO)
    panel_h = config.TARGET_H - source_h

    base = VideoFileClip(source_path)
    duration = min(config.MAX_CLIP_SECONDS, base.duration)
    base = base.subclipped(0, duration)
    fitted = _fit_and_crop(base, config.TARGET_W, source_h).with_position((0, 0))

    panel_img = _build_caption_panel(script_text, config.TARGET_W, panel_h, rtl)
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
