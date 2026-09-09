"""Shared Pillow helpers for burning text onto a 1080-wide canvas -- used by
both video_composer.py (text-over-video Reels) and image_composer.py
(static feed/story cards). Kept dependency-free of moviepy/ImageMagick.
"""
import os
import textwrap

from PIL import ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, font, box_left: int, box_top: int,
                  fill, line_spacing: int = 12, max_width_chars: int = 26) -> int:
    """Draw word-wrapped text starting at (box_left, box_top). Returns the
    y-coordinate just below the last line, so callers can stack panels."""
    lines = textwrap.wrap(text, width=max_width_chars)
    y = box_top
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_h = bbox[3] - bbox[1]
        draw.text((box_left, y), line, font=font, fill=fill)
        y += line_h + line_spacing
    return y


def rounded_panel(draw: ImageDraw.ImageDraw, xy, fill, radius: int = 28) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill)
