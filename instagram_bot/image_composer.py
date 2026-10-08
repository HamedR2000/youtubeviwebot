"""Render a single branded card (feed image post, 4:5, or story, 9:16) --
either "dark" (a background photo + text overlay) or "light" (flat cream,
no photo), matching carousel_composer.py's two moods (see theme.py), so
content doesn't read as uniformly dark across the whole account.

Uses the same Montserrat/Playfair Display fonts as carousel_composer.py
for a consistent premium look across carousel, story and feed cards.
"""
from PIL import Image, ImageDraw

from icon_kit import draw_icon
from text_overlay import draw_wrapped_px, draw_wrapped_rtl, montserrat, playfair, rounded_panel, vazirmatn
from theme import THEMES, add_sparkle_accents, flat_light_background

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
    canvas = Image.alpha_composite(bg.convert("RGBA"), dark)
    # The light theme already got a glittery, "busier" treatment (see
    # theme.flat_light_background) after the account owner felt the first
    # version was too plain -- the dark theme leaned on its hero photo
    # alone, which read as plain again once the owner compared it against
    # other accounts in the same niche. Same sparkle layer here keeps both
    # moods equally rich.
    add_sparkle_accents(canvas, w, h)
    return canvas


def _topic_badge(draw: ImageDraw.ImageDraw, topic: str, t: dict, w: int, margin: int, rtl: bool) -> None:
    """A pill-shaped badge (icon + label) instead of plain uppercase text --
    closer to how other accounts in the gold/forex niche tag their story
    topic, and reads as more "designed" than a bare line of text."""
    font = vazirmatn(24, "Bold") if rtl else montserrat(24, "SemiBold")
    label = topic if rtl else topic.upper()
    text_w = draw.textlength(label, font=font, direction="rtl", language="fa") if rtl \
        else draw.textlength(label, font=font)
    icon_r = 14
    pad_x, pad_icon = 22, 14
    badge_h = 52
    badge_w = pad_x * 2 + icon_r * 2 + pad_icon + text_w
    badge_y0 = 56

    if rtl:
        badge_x1 = w - margin
        badge_x0 = badge_x1 - badge_w
    else:
        badge_x0 = margin
        badge_x1 = badge_x0 + badge_w

    draw.rounded_rectangle([badge_x0, badge_y0, badge_x1, badge_y0 + badge_h],
                            radius=badge_h / 2, fill=(*t["gold"][:3], 46),
                            outline=t["gold_bright"], width=1)
    badge_cy = badge_y0 + badge_h / 2
    if rtl:
        icon_cx = badge_x1 - pad_x - icon_r
        draw_icon("trend_up", draw, icon_cx, badge_cy, icon_r, t["gold_bright"])
        text_x = icon_cx - icon_r - pad_icon - text_w
        draw.text((text_x, badge_cy - 14), label, font=font,
                   fill=t["gold_bright"], direction="rtl", language="fa")
    else:
        icon_cx = badge_x0 + pad_x + icon_r
        draw_icon("trend_up", draw, icon_cx, badge_cy, icon_r, t["gold_bright"])
        draw.text((icon_cx + icon_r + pad_icon, badge_cy - 14), label, font=font, fill=t["gold_bright"])


def build_feed_card(photo_path: str, headline: str, subtitle: str, cta: str,
                     brand_handle: str, output_path: str, theme: str = "dark",
                     rtl: bool = False) -> None:
    """rtl=True renders headline/subtitle/cta with the Persian/Arabic-script
    font, shaped and right-aligned -- used on Persian-language days (see
    ENGLISH_WEEKDAYS in main.py). brand_handle stays Latin/LTR either way,
    same as build_story_card."""
    t = THEMES[theme]
    w, h = FEED_SIZE
    canvas = _base_canvas(photo_path, w, h, theme)
    draw = ImageDraw.Draw(canvas)

    margin = 72
    brand_font = montserrat(32, "SemiBold")
    shadow = t["shadow"] if theme == "dark" else None

    if rtl:
        headline_font = vazirmatn(52, "Bold")
        subtitle_font = vazirmatn(32, "Regular")
        cta_font = vazirmatn(28, "Bold")
        right_x = w - margin
        y = draw_wrapped_rtl(draw, headline, headline_font, right_x, 140, w - 2 * margin,
                              fill=t["heading"], line_spacing=14, shadow=shadow)
        y = draw_wrapped_rtl(draw, subtitle, subtitle_font, right_x, y + 40, w - 2 * margin,
                              fill=t["body"], line_spacing=10, shadow=shadow)
    else:
        headline_font = playfair(66, "Bold")
        subtitle_font = montserrat(38, "Regular")
        cta_font = montserrat(34, "SemiBold")
        y = draw_wrapped_px(draw, headline, headline_font, margin, 140, w - 2 * margin,
                             fill=t["heading"], line_spacing=14, shadow=shadow)
        y = draw_wrapped_px(draw, subtitle, subtitle_font, margin, y + 40, w - 2 * margin,
                             fill=t["body"], line_spacing=10, shadow=shadow)

    outline = {"outline": t["cta_outline"], "width": 2} if t["cta_outline"] else {}
    rounded_panel(draw, [margin, h - 220, w - margin, h - 140], t["cta_fill"])
    if outline:
        draw.rounded_rectangle([margin, h - 220, w - margin, h - 140], radius=28, **outline)
    if rtl:
        cta_w = draw.textlength(cta, font=cta_font, direction="rtl", language="fa")
        draw.text((w - margin - 24 - cta_w, h - 205), cta, font=cta_font, fill=t["cta_text"],
                   direction="rtl", language="fa")
    else:
        draw.text((margin + 24, h - 205), cta, font=cta_font, fill=t["cta_text"])

    draw.text((margin, h - 90), brand_handle, font=brand_font, fill=t["gold_bright"])

    canvas.convert("RGB").save(output_path, quality=90)


def build_story_card(photo_path: str, line: str, brand_handle: str, output_path: str,
                      rtl: bool = False, theme: str = "dark",
                      topic: str = None, page_num: int = None, page_total: int = None) -> None:
    """rtl=True renders `line` with the Persian/Arabic-script font, shaped
    and right-aligned. topic/page_num/page_total (all optional) draw a
    small kicker + counter at the top -- so the STORIES_PER_DAY slides of
    one content_bank.STORY_SETS entry visibly read as one connected
    thread instead of disconnected one-liners."""
    t = THEMES[theme]
    w, h = STORY_SIZE
    canvas = _base_canvas(photo_path, w, h, theme)
    draw = ImageDraw.Draw(canvas)

    margin = 80
    brand_font = montserrat(34, "SemiBold")
    shadow = t["shadow"] if theme == "dark" else None

    if topic:
        _topic_badge(draw, topic, t, w, margin, rtl)

    if page_num and page_total:
        counter_font = montserrat(24, "SemiBold")
        counter_text = f"{page_num}/{page_total}"
        cw = draw.textlength(counter_text, font=counter_font)
        cx = margin if rtl else w - margin - cw
        draw.text((cx, 72), counter_text, font=counter_font, fill=t["muted"])

    # A short gold rule above the headline gives the slide more visual
    # structure than a line of text floating with nothing around it --
    # same device the carousel slides use above their body paragraph.
    rule_y = h // 2 - 170
    if rtl:
        draw.line([(w - margin, rule_y), (w - margin - 60, rule_y)], fill=t["gold"], width=2)
    else:
        draw.line([(margin, rule_y), (margin + 60, rule_y)], fill=t["gold"], width=2)

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

    # Small market-tag sticker next to the brand handle (XAUUSD / GOLD),
    # mimicking the little topic/asset stickers other finance-niche
    # accounts put on their stories -- a static design element, since
    # Stories posted through the Graph API can't carry real interactive
    # stickers.
    tag_font = montserrat(22, "Bold")
    tag_text = "XAUUSD"
    tag_w = draw.textlength(tag_text, font=tag_font)
    tag_pad_x, tag_h = 20, 44
    if rtl:
        tag_x1 = w - margin
        tag_x0 = tag_x1 - (tag_w + 2 * tag_pad_x)
    else:
        tag_x0 = margin
        tag_x1 = tag_x0 + tag_w + 2 * tag_pad_x
    tag_y0 = h - 200
    draw.rounded_rectangle([tag_x0, tag_y0, tag_x1, tag_y0 + tag_h], radius=tag_h / 2,
                            fill=t["cta_fill"])
    draw.text((tag_x0 + tag_pad_x, tag_y0 + (tag_h - 28) / 2), tag_text, font=tag_font,
               fill=t["cta_text"])

    canvas.convert("RGB").save(output_path, quality=90)


def build_reel_cover(photo_path: str, hook: str, brand_handle: str, output_path: str,
                      rtl: bool = False, theme: str = "dark") -> None:
    """A dedicated, static cover image for a Reel, used as the Graph API's
    cover_url so the profile grid tile shows a bold designed headline
    instead of a random auto-picked frame from the raw stock clip (the
    account owner's complaint: reels had no attention-grabbing cover on
    the profile at all). Text is kept inside a vertical band roughly
    y=[440, 1480] of the 1080x1920 canvas, which survives Instagram's own
    center-crop of the full reel frame into whatever aspect it shows in
    the grid, be that square or 4:5."""
    t = THEMES[theme]
    w, h = STORY_SIZE
    canvas = _base_canvas(photo_path, w, h, theme)
    draw = ImageDraw.Draw(canvas)

    margin = 90
    shadow = t["shadow"] if theme == "dark" else None

    badge_font = montserrat(26, "Bold")
    badge_text = "GOLD SIGNALS"
    badge_w = draw.textlength(badge_text, font=badge_font)
    badge_pad_x, badge_h = 26, 56
    badge_x0 = (w - (badge_w + 2 * badge_pad_x)) / 2
    badge_y0 = 500
    draw.rounded_rectangle([badge_x0, badge_y0, badge_x0 + badge_w + 2 * badge_pad_x, badge_y0 + badge_h],
                            radius=badge_h / 2, fill=t["cta_fill"], outline=t["gold_bright"], width=2)
    draw.text((badge_x0 + badge_pad_x, badge_y0 + (badge_h - 32) / 2), badge_text, font=badge_font,
               fill=t["cta_text"])

    headline_y = badge_y0 + badge_h + 60
    if rtl:
        headline_font = vazirmatn(72, "Bold")
        lines = []
        words = hook.split()
        cur = ""
        for word in words:
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=headline_font, direction="rtl", language="fa") <= w - 2 * margin or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        y = headline_y
        for ln in lines:
            lw = draw.textlength(ln, font=headline_font, direction="rtl", language="fa")
            lx = (w - lw) / 2
            if shadow:
                draw.text((lx + 3, y + 3), ln, font=headline_font, fill=shadow, direction="rtl", language="fa")
            draw.text((lx, y), ln, font=headline_font, fill=t["heading"], direction="rtl", language="fa")
            bbox = draw.textbbox((0, 0), ln, font=headline_font, direction="rtl", language="fa")
            y += (bbox[3] - bbox[1]) + 20
    else:
        headline_font = playfair(76, "Bold")
        y = draw_wrapped_px(draw, hook, headline_font, w / 2, headline_y, w - 2 * margin,
                             fill=t["heading"], line_spacing=20, align="center", shadow=shadow)

    brand_font = montserrat(32, "SemiBold")
    bw = draw.textlength(brand_handle, font=brand_font)
    draw.text(((w - bw) / 2, 1400), brand_handle, font=brand_font, fill=t["gold_bright"])

    canvas.convert("RGB").save(output_path, quality=92)
