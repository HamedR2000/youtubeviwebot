"""Render a single branded card (feed image post, 4:5, or story, 9:16) --
either "dark" (a background photo + text overlay) or "light" (flat cream,
no photo), matching carousel_composer.py's two moods (see theme.py), so
content doesn't read as uniformly dark across the whole account.

Uses the same Montserrat/Playfair Display fonts as carousel_composer.py
for a consistent premium look across carousel, story and feed cards.
"""
from PIL import Image, ImageDraw

from text_overlay import draw_wrapped_px, draw_wrapped_rtl, montserrat, playfair, rounded_panel, vazirmatn
from theme import THEMES, flat_light_background

FEED_SIZE = (1080, 1350)   # Instagram feed portrait (4:5)
STORY_SIZE = (1080, 1920)  # Instagram story/reel (9:16)

DARKEN_ALPHA = 130  # 0-255, how much black overlay to lay over the dark theme's photo for legibility


def _cover_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    scale = max(target_w / img.width, target_h / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)))
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def _base_canvas(photo_path: str, w: int, h: int, theme: str) -> Image.Image:
    if theme == "light":
        return flat_light_background(w, h)
    bg = _cover_crop(Image.open(photo_path).convert("RGB"), w, h)
    dark = Image.new("RGBA", (w, h), (0, 0, 0, DARKEN_ALPHA))
    return Image.alpha_composite(bg.convert("RGBA"), dark)


def build_feed_card(photo_path: str, headline: str, subtitle: str, cta: str,
                     brand_handle: str, output_path: str, theme: str = "dark") -> None:
    t = THEMES[theme]
    w, h = FEED_SIZE
    canvas = _base_canvas(photo_path, w, h, theme)
    draw = ImageDraw.Draw(canvas)

    margin = 72
    headline_font = playfair(66, "Bold")
    subtitle_font = montserrat(38, "Regular")
    cta_font = montserrat(34, "SemiBold")
    brand_font = montserrat(32, "SemiBold")
    shadow = t["shadow"] if theme == "dark" else None

    y = draw_wrapped_px(draw, headline, headline_font, margin, 140, w - 2 * margin,
                         fill=t["heading"], line_spacing=14, shadow=shadow)
    y = draw_wrapped_px(draw, subtitle, subtitle_font, margin, y + 40, w - 2 * margin,
                         fill=t["body"], line_spacing=10, shadow=shadow)

    outline = {"outline": t["cta_outline"], "width": 2} if t["cta_outline"] else {}
    rounded_panel(draw, [margin, h - 220, w - margin, h - 140], t["cta_fill"])
    if outline:
        draw.rounded_rectangle([margin, h - 220, w - margin, h - 140], radius=28, **outline)
    draw.text((margin + 24, h - 205), cta, font=cta_font, fill=t["cta_text"])

    draw.text((margin, h - 90), brand_handle, font=brand_font, fill=t["gold_bright"])

    canvas.convert("RGB").save(output_path, quality=90)


def build_story_card(photo_path: str, line: str, brand_handle: str, output_path: str,
                      rtl: bool = False, theme: str = "dark") -> None:
    """rtl=True renders `line` with the Persian/Arabic-script font, shaped
    and right-aligned -- used for the once-a-week Persian story."""
    t = THEMES[theme]
    w, h = STORY_SIZE
    canvas = _base_canvas(photo_path, w, h, theme)
    draw = ImageDraw.Draw(canvas)

    margin = 80
    brand_font = montserrat(34, "SemiBold")
    shadow = t["shadow"] if theme == "dark" else None

    # Vertically centered single line/short block -- stories are meant to be
    # read in ~2 seconds.
    if rtl:
        line_font = vazirmatn(60, "Bold")
        draw_wrapped_rtl(draw, line, line_font, w - margin, h // 2 - 120, w - 2 * margin,
                          fill=t["heading"], line_spacing=16, shadow=shadow)
    else:
        line_font = playfair(62, "Bold")
        draw_wrapped_px(draw, line, line_font, margin, h // 2 - 120, w - 2 * margin,
                         fill=t["heading"], line_spacing=16, shadow=shadow)

    draw.text((margin, h - 140), brand_handle, font=brand_font, fill=t["gold_bright"])

    canvas.convert("RGB").save(output_path, quality=90)
