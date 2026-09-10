"""Shared Pillow helpers for burning text onto a 1080-wide canvas -- used by
both video_composer.py (text-over-video Reels) and image_composer.py
(static feed/story cards). Kept dependency-free of moviepy/ImageMagick.
"""
import os
import textwrap

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
MONTSERRAT_PATH = os.path.join(FONT_DIR, "Montserrat[wght].ttf")
PLAYFAIR_PATH = os.path.join(FONT_DIR, "PlayfairDisplay[wght].ttf")
VAZIRMATN_PATH = os.path.join(FONT_DIR, "Vazirmatn[wght].ttf")


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _variable_font(path: str, size: int, variation: str) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_name(variation)
    except Exception:
        pass
    return f


def montserrat(size: int, weight: str = "Regular") -> ImageFont.FreeTypeFont:
    """The same body/UI font used by the carousel slides, for visual
    consistency across carousel, story and feed cards."""
    return _variable_font(MONTSERRAT_PATH, size, weight)


def playfair(size: int, weight: str = "Bold") -> ImageFont.FreeTypeFont:
    """The same serif headline font used by the carousel slides."""
    return _variable_font(PLAYFAIR_PATH, size, weight)


def vazirmatn(size: int, weight: str = "Bold") -> ImageFont.FreeTypeFont:
    """Persian/Arabic-script font, used for the once-a-week Persian story."""
    return _variable_font(VAZIRMATN_PATH, size, weight)


def shape_rtl(text: str) -> str:
    """Reshape + reorder Persian/Arabic text for correct glyph joining and
    right-to-left display -- Pillow draws Unicode code points as given, it
    does not do this itself."""
    return get_display(arabic_reshaper.reshape(text))


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


def wrap_lines_px(draw: ImageDraw.ImageDraw, text: str, font, max_width_px: int) -> list:
    """Word-wrap `text` to `max_width_px`, measuring actual glyph width
    (unlike draw_wrapped's char-count wrap, which is a poor fit for
    variable-width fonts like Playfair Display)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped_rtl(draw: ImageDraw.ImageDraw, text: str, font, right_x: int, y: int,
                      max_width_px: int, fill, line_spacing: int = 10, shadow=None) -> int:
    """Word-wrap + draw right-to-left Persian/Arabic text, right-aligned to
    `right_x`. Wrapping splits the logical (unshaped) string on spaces --
    correct for space-separated Persian words -- then each finished line is
    reshaped for display. Returns the y-coordinate just below the last line."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(shape_rtl(trial), font=font) <= max_width_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    for line in lines:
        shaped = shape_rtl(line)
        line_x = right_x - draw.textlength(shaped, font=font)
        if shadow:
            draw.text((line_x + 2, y + 2), shaped, font=font, fill=shadow)
        draw.text((line_x, y), shaped, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), shaped, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y


def draw_wrapped_px(draw: ImageDraw.ImageDraw, text: str, font, x: int, y: int,
                     max_width_px: int, fill, line_spacing: int = 10,
                     align: str = "left", shadow=None) -> int:
    """Pixel-width word-wrap + draw, with optional drop shadow (pass a fill
    color) so text stays legible over a photo of unpredictable brightness.
    Returns the y-coordinate just below the last line."""
    lines = wrap_lines_px(draw, text, font, max_width_px)
    for line in lines:
        line_x = x
        if align == "center":
            line_x = x - draw.textlength(line, font=font) / 2
        if shadow:
            draw.text((line_x + 2, y + 2), line, font=font, fill=shadow)
        draw.text((line_x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y
