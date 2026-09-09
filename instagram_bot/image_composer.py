"""Render a single branded card (feed image post, 4:5, or story, 9:16) from
a Pexels photo background plus a Pillow text overlay. Reused for both feed
posts (headline + subtitle + CTA) and story cards (one short line + brand).
"""
from PIL import Image, ImageDraw

from text_overlay import draw_wrapped, load_font, rounded_panel

FEED_SIZE = (1080, 1350)   # Instagram feed portrait (4:5)
STORY_SIZE = (1080, 1920)  # Instagram story/reel (9:16)

DARKEN_ALPHA = 130  # 0-255, how much black overlay to lay over the photo for text legibility


def _cover_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    scale = max(target_w / img.width, target_h / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)))
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def build_feed_card(photo_path: str, headline: str, subtitle: str, cta: str,
                     brand_handle: str, output_path: str) -> None:
    w, h = FEED_SIZE
    bg = _cover_crop(Image.open(photo_path).convert("RGB"), w, h)
    dark = Image.new("RGBA", (w, h), (0, 0, 0, DARKEN_ALPHA))
    canvas = Image.alpha_composite(bg.convert("RGBA"), dark)
    draw = ImageDraw.Draw(canvas)

    margin = 72
    headline_font = load_font(72)
    subtitle_font = load_font(42)
    cta_font = load_font(36)
    brand_font = load_font(34)

    y = draw_wrapped(draw, headline, headline_font, margin, 140,
                      fill=(255, 215, 0, 255), max_width_chars=18, line_spacing=14)
    y = draw_wrapped(draw, subtitle, subtitle_font, margin, y + 40,
                      fill=(255, 255, 255, 255), max_width_chars=32, line_spacing=10)

    rounded_panel(draw, [margin, h - 220, w - margin, h - 140], (255, 215, 0, 230))
    draw.text((margin + 24, h - 205), cta, font=cta_font, fill=(20, 20, 20, 255))

    draw.text((margin, h - 90), brand_handle, font=brand_font, fill=(255, 255, 255, 255))

    canvas.convert("RGB").save(output_path, quality=90)


def build_story_card(photo_path: str, line: str, brand_handle: str, output_path: str) -> None:
    w, h = STORY_SIZE
    bg = _cover_crop(Image.open(photo_path).convert("RGB"), w, h)
    dark = Image.new("RGBA", (w, h), (0, 0, 0, DARKEN_ALPHA))
    canvas = Image.alpha_composite(bg.convert("RGBA"), dark)
    draw = ImageDraw.Draw(canvas)

    margin = 80
    line_font = load_font(68)
    brand_font = load_font(38)

    # Vertically centered single line/short block -- stories are meant to be
    # read in ~2 seconds.
    draw_wrapped(draw, line, line_font, margin, h // 2 - 120,
                 fill=(255, 255, 255, 255), max_width_chars=20, line_spacing=16)

    draw.text((margin, h - 140), brand_handle, font=brand_font, fill=(255, 215, 0, 255))

    canvas.convert("RGB").save(output_path, quality=90)
