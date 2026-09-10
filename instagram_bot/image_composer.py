"""Render a single branded card (feed image post, 4:5, or story, 9:16) from
a background photo plus a Pillow text overlay. Reused for both feed posts
(headline + subtitle + CTA) and story cards (one short line + brand).

Uses the same Montserrat/Playfair Display fonts and gold/cream palette as
carousel_composer.py, so Stories and feed posts share the carousel's
premium look rather than the plain system-font style they used before.
"""
from PIL import Image, ImageDraw

from text_overlay import draw_wrapped_px, draw_wrapped_rtl, montserrat, playfair, rounded_panel, vazirmatn

FEED_SIZE = (1080, 1350)   # Instagram feed portrait (4:5)
STORY_SIZE = (1080, 1920)  # Instagram story/reel (9:16)

DARKEN_ALPHA = 130  # 0-255, how much black overlay to lay over the photo for text legibility

CREAM = (240, 235, 225, 255)
GOLD = (196, 155, 98, 255)
GOLD_BRIGHT = (214, 175, 116, 255)
SHADOW = (0, 0, 0, 170)


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
    headline_font = playfair(66, "Bold")
    subtitle_font = montserrat(38, "Regular")
    cta_font = montserrat(34, "SemiBold")
    brand_font = montserrat(32, "SemiBold")

    y = draw_wrapped_px(draw, headline, headline_font, margin, 140, w - 2 * margin,
                         fill=CREAM, line_spacing=14, shadow=SHADOW)
    y = draw_wrapped_px(draw, subtitle, subtitle_font, margin, y + 40, w - 2 * margin,
                         fill=(225, 221, 214, 255), line_spacing=10, shadow=SHADOW)

    rounded_panel(draw, [margin, h - 220, w - margin, h - 140], GOLD)
    draw.text((margin + 24, h - 205), cta, font=cta_font, fill=(20, 16, 12, 255))

    draw.text((margin, h - 90), brand_handle, font=brand_font, fill=GOLD_BRIGHT)

    canvas.convert("RGB").save(output_path, quality=90)


def build_story_card(photo_path: str, line: str, brand_handle: str, output_path: str,
                      rtl: bool = False) -> None:
    """rtl=True renders `line` with the Persian/Arabic-script font, shaped
    and right-aligned -- used for the once-a-week Persian story."""
    w, h = STORY_SIZE
    bg = _cover_crop(Image.open(photo_path).convert("RGB"), w, h)
    dark = Image.new("RGBA", (w, h), (0, 0, 0, DARKEN_ALPHA))
    canvas = Image.alpha_composite(bg.convert("RGBA"), dark)
    draw = ImageDraw.Draw(canvas)

    margin = 80
    brand_font = montserrat(34, "SemiBold")

    # Vertically centered single line/short block -- stories are meant to be
    # read in ~2 seconds.
    if rtl:
        line_font = vazirmatn(60, "Bold")
        draw_wrapped_rtl(draw, line, line_font, w - margin, h // 2 - 120, w - 2 * margin,
                          fill=CREAM, line_spacing=16, shadow=SHADOW)
    else:
        line_font = playfair(62, "Bold")
        draw_wrapped_px(draw, line, line_font, margin, h // 2 - 120, w - 2 * margin,
                         fill=CREAM, line_spacing=16, shadow=SHADOW)

    draw.text((margin, h - 140), brand_handle, font=brand_font, fill=GOLD_BRIGHT)

    canvas.convert("RGB").save(output_path, quality=90)
