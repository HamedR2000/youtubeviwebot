"""Renders one slide of a premium educational carousel in one of two moods
(see theme.py): "dark" (near-black + a hero photo, the original look) or
"light" (warm cream/gold, no photo) -- added after the account owner asked
for content that isn't uniformly dark. Both share the same layout: top
category tag + a page counter, decorative micro-taglines, a two-tone serif
headline, a body paragraph, a 3-column row of circled line-icons (label +
short caption, divided by thin rules), a takeaway line, and a bottom CTA
pill with a small icon.

Uses Montserrat (UI/body) + Playfair Display (serif headline) -- both
bundled under fonts/ as OFL-licensed variable fonts -- and icon_kit.py for
the circled line icons. No external image assets besides the optional
hero photo.
"""
from PIL import Image, ImageDraw

from icon_kit import draw_icon
from text_overlay import draw_wrapped_px, montserrat, playfair, vazirmatn, wrap_lines_px
from theme import THEMES, flat_light_background

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 70


def _tracked_width(draw, text, font, tracking):
    if not text:
        return 0
    total = 0
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        total += (bbox[2] - bbox[0]) + tracking
    return total - tracking


def draw_tracked_text(draw, xy, text, font, fill, tracking=0, anchor_right=False):
    x, y = xy
    if anchor_right:
        x -= _tracked_width(draw, text, font, tracking)
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), ch, font=font)
        x += (bbox[2] - bbox[0]) + tracking
    return x


def _wrap_lines(draw, text, font, max_width_px):
    return wrap_lines_px(draw, text, font, max_width_px)


def _wrap_draw(draw, text, font, x, y, max_width_px, fill, line_spacing=10,
               align="left", shadow=None):
    return draw_wrapped_px(draw, text, font, x, y, max_width_px, fill,
                            line_spacing=line_spacing, align=align, shadow=shadow)


def _wrap_lines_rtl(draw, text, font, max_width_px):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        width = draw.textlength(trial, font=font, direction="rtl", language="fa")
        if width <= max_width_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _wrap_draw_rtl(draw, text, font, x, y, max_width_px, fill, line_spacing=10,
                    align="right", shadow=None):
    """Persian/Arabic-script counterpart to _wrap_draw: same signature (so
    callers can pick one of the two with `fn = _wrap_draw_rtl if rtl else
    _wrap_draw`), but wraps by RTL-shaped width and draws right-to-left.
    align="right" anchors the block's right edge at x; "center" centers on x.
    """
    lines = _wrap_lines_rtl(draw, text, font, max_width_px)
    for line in lines:
        line_w = draw.textlength(line, font=font, direction="rtl", language="fa")
        line_x = x - line_w / 2 if align == "center" else x - line_w
        if shadow:
            draw.text((line_x + 2, y + 2), line, font=font, fill=shadow, direction="rtl", language="fa")
        draw.text((line_x, y), line, font=font, fill=fill, direction="rtl", language="fa")
        bbox = draw.textbbox((0, 0), line, font=font, direction="rtl", language="fa")
        y += (bbox[3] - bbox[1]) + line_spacing
    return y


def _text_len(draw, text, font, rtl):
    return draw.textlength(text, font=font, direction="rtl", language="fa") if rtl else draw.textlength(text, font=font)


def _text_bbox(draw, text, font, rtl):
    if rtl:
        return draw.textbbox((0, 0), text, font=font, direction="rtl", language="fa")
    return draw.textbbox((0, 0), text, font=font)


def _draw_text(draw, xy, text, font, fill, rtl):
    if rtl:
        draw.text(xy, text, font=font, fill=fill, direction="rtl", language="fa")
    else:
        draw.text(xy, text, font=font, fill=fill)


def _cover_crop(img, w, h):
    scale = max(w / img.width, h / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)))
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


HERO_H = 620          # height of the photo region, anchored to the bottom
HERO_FEATHER = 220    # how tall the fade-to-dark transition at its top edge is


def _background_dark(photo_path):
    """Solid near-black canvas with the subject photo confined to the lower
    ~46% of the frame (feathered into the dark background at its top edge),
    matching the reference template -- rather than one full-bleed photo
    dimmed everywhere, which read as a generic dark texture instead of
    clearly being about gold/trading.
    """
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (10, 8, 9, 255))

    # Faint warm glow behind where the hero photo will sit, so the
    # transition into the photo feels intentional rather than abrupt.
    glow = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gcx, gcy, gr = CANVAS_W // 2, CANVAS_H - HERO_H // 2, int(CANVAS_W * 0.75)
    gd.ellipse([gcx - gr, gcy - gr, gcx + gr, gcy + gr], fill=(110, 60, 60, 40))
    canvas.alpha_composite(glow)

    hero = _cover_crop(Image.open(photo_path).convert("RGB"), CANVAS_W, HERO_H).convert("RGBA")
    mask = Image.new("L", (CANVAS_W, HERO_H), 255)
    md = ImageDraw.Draw(mask)
    for y in range(HERO_FEATHER):
        a = int(255 * (y / HERO_FEATHER))
        md.line([(0, y), (CANVAS_W, y)], fill=a)
    hero.putalpha(mask)
    canvas.alpha_composite(hero, (0, CANVAS_H - HERO_H))

    # Bottom vignette (graduated, strongest right at the edge) so the plain
    # corner micro-tags stay readable no matter how bright the photo is.
    fade_h = 190
    vignette = Image.new("L", (CANVAS_W, CANVAS_H), 0)
    vd = ImageDraw.Draw(vignette)
    for i in range(fade_h):
        y = CANVAS_H - fade_h + i
        a = int(190 * (i / fade_h))
        vd.line([(0, y), (CANVAS_W, y)], fill=a)
    dark = Image.new("RGBA", (CANVAS_W, CANVAS_H), (2, 2, 3, 255))
    canvas = Image.composite(dark, canvas, vignette)
    return canvas


def build_slide(
    photo_path: str,
    output_path: str,
    category_label: str,
    page_num: int,
    page_total: int,
    headline_lines: list,       # [(text, "white"|"gold"), ...]
    body_text: str,
    panels: list,               # [(icon_name, title, desc), ...] up to 3, rendered as columns
    takeaway_text: str,
    cta_text: str,
    top_left_tagline: tuple = None,   # (line1, line2)
    top_right_words: list = None,     # small stacked words, e.g. ["SAME","MARKETS"]
    corner_left_words: list = None,   # e.g. ["ANALYZE","PLAN","EXECUTE"]
    corner_right_words: list = None,  # e.g. ["GOLD","DISCIPLINE","FREEDOM"]
    theme: str = "dark",              # "dark" (hero photo) or "light" (flat cream, no photo)
    rtl: bool = False,                # True renders all text Persian/Arabic-script, shaped + RTL
) -> None:
    t = THEMES[theme]
    heading, heading_accent = t["heading"], t["heading_accent"]
    body_c, muted, gold = t["body"], t["muted"], t["gold"]
    shadow = t["shadow"]

    canvas = flat_light_background(CANVAS_W, CANVAS_H) if theme == "light" else _background_dark(photo_path)
    draw = ImageDraw.Draw(canvas)

    # -- top row: category tag (left) + page counter (right) --
    if rtl:
        cat_font = vazirmatn(26, "Bold")
        draw.text((MARGIN, 52), category_label, font=cat_font, fill=heading, direction="rtl", language="fa")
    else:
        cat_font = montserrat(28, "SemiBold")
        draw_tracked_text(draw, (MARGIN, 52), category_label.upper(), cat_font, heading, tracking=2)

    counter_font = montserrat(30, "Bold")
    counter_text = f"{page_num}/{page_total}"
    r = 44
    ccx, ccy = CANVAS_W - MARGIN - r, 50 + r
    bbox = draw.textbbox((0, 0), counter_text, font=counter_font)
    cw = draw.textlength(counter_text, font=counter_font)
    if t["counter_style"] == "pill":
        draw.rounded_rectangle([ccx - r, ccy - r * 0.7, ccx + r, ccy + r * 0.7],
                                radius=r * 0.7, fill=t["cta_fill"])
        draw.text((ccx - cw / 2, ccy - (bbox[3] - bbox[1]) / 2 - bbox[1]), counter_text,
                   font=counter_font, fill=t["cta_text"])
    else:
        draw.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], outline=heading, width=2)
        draw.text((ccx - cw / 2, ccy - (bbox[3] - bbox[1]) / 2 - bbox[1]), counter_text,
                   font=counter_font, fill=heading)

    # -- decorative micro-taglines --
    tag_font = vazirmatn(19, "Bold") if rtl else montserrat(20, "Regular")
    if top_left_tagline:
        draw.line([(MARGIN, 130), (MARGIN + 34, 130)], fill=gold, width=2)
        ty = 140
        for line in top_left_tagline:
            if rtl:
                draw.text((MARGIN, ty), line, font=tag_font, fill=muted, direction="rtl", language="fa")
            else:
                draw_tracked_text(draw, (MARGIN, ty), line.upper(), tag_font, muted, tracking=2)
            ty += 26

    if top_right_words:
        ty = 140
        for w in top_right_words:
            if rtl:
                tw = _text_len(draw, w, tag_font, rtl)
                draw.text((CANVAS_W - MARGIN - tw, ty), w, font=tag_font, fill=muted, direction="rtl", language="fa")
            else:
                draw_tracked_text(draw, (CANVAS_W - MARGIN, ty), w.upper(), tag_font, muted,
                                   tracking=2, anchor_right=True)
            ty += 26

    # -- headline: serif (Latin) or Vazirmatn (Persian), two-tone,
    #    word-wrapped so long phrases never spill off the canvas edge.
    #    RTL right-aligns the block to the right margin instead. --
    head_font = vazirmatn(58, "Bold") if rtl else playfair(70, "Bold")
    headline_max_w = CANVAS_W - 2 * MARGIN
    head_x = CANVAS_W - MARGIN if rtl else MARGIN
    hy = 300
    wrap_fn = _wrap_draw_rtl if rtl else _wrap_draw
    for text, tone in headline_lines:
        color = heading_accent if tone == "gold" else heading
        hy = wrap_fn(draw, text, head_font, head_x, hy, headline_max_w, color, line_spacing=16)

    hy += 14
    if rtl:
        draw.line([(CANVAS_W - MARGIN, hy), (CANVAS_W - MARGIN - 60, hy)], fill=gold, width=2)
    else:
        draw.line([(MARGIN, hy), (MARGIN + 60, hy)], fill=gold, width=2)
    hy += 26

    # -- body paragraph --
    body_font = vazirmatn(28, "Regular") if rtl else montserrat(33, "Regular")
    body_w = CANVAS_W - 2 * MARGIN
    by = wrap_fn(draw, body_text, body_font, head_x, hy, body_w, body_c, line_spacing=10)

    # -- 3-column icon row: circled icon, bold label, short caption, thin
    #    vertical dividers between columns. Dark theme drop-shadows this
    #    section since it can sit over the hero photo; light theme's flat
    #    background doesn't need it. --
    panel_top = by + 46
    n = max(len(panels), 1)
    col_w = (CANVAS_W - 2 * MARGIN) / n
    icon_r = 34
    label_font = vazirmatn(26, "Bold") if rtl else montserrat(30, "Bold")
    desc_font = vazirmatn(19, "Regular") if rtl else montserrat(23, "Regular")
    col_bottom = panel_top

    for idx, (icon_name, title, desc) in enumerate(panels):
        col_cx = MARGIN + col_w * idx + col_w / 2
        icon_cy = panel_top + icon_r + 4

        if theme == "dark":
            shadow_disc = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shadow_disc)
            sd.ellipse([col_cx - icon_r - 8, icon_cy - icon_r - 8, col_cx + icon_r + 8, icon_cy + icon_r + 8],
                       fill=(0, 0, 0, 110))
            canvas.alpha_composite(shadow_disc)
            draw = ImageDraw.Draw(canvas)
        draw_icon(icon_name, draw, col_cx, icon_cy, icon_r, heading_accent)

        label_y = icon_cy + icon_r + 22
        label_w = _text_len(draw, title, label_font, rtl)
        _draw_text(draw, (col_cx - label_w / 2 + 1, label_y + 1), title, label_font, shadow, rtl)
        _draw_text(draw, (col_cx - label_w / 2, label_y), title, label_font, heading, rtl)
        bbox = _text_bbox(draw, title, label_font, rtl)
        desc_y = label_y + (bbox[3] - bbox[1]) + 10

        desc_bottom = wrap_fn(draw, desc, desc_font, col_cx, desc_y, col_w - 28, muted,
                               line_spacing=6, align="center",
                               shadow=shadow if theme == "dark" else None)
        col_bottom = max(col_bottom, desc_bottom)

        if idx > 0:
            div_x = MARGIN + col_w * idx
            draw.line([(div_x, panel_top + 4), (div_x, col_bottom - 6)], fill=(*gold[:3], 90), width=1)

    # -- takeaway line: short gold divider, then centered text --
    take_y = col_bottom + 34
    draw.line([(CANVAS_W / 2 - 30, take_y), (CANVAS_W / 2 + 30, take_y)], fill=gold, width=2)
    take_y += 20
    take_font = vazirmatn(28, "Bold") if rtl else montserrat(32, "SemiBold")
    take_bottom = wrap_fn(draw, takeaway_text, take_font, CANVAS_W / 2, take_y,
                           CANVAS_W - 2 * MARGIN - 60, heading, line_spacing=8,
                           align="center", shadow=shadow if theme == "dark" else None)

    # -- bottom CTA pill (centered, small icon + text + arrow). RTL mirrors
    #    the pill: icon+arrow move to the right/left ends respectively, and
    #    the Persian text is measured/drawn with direction="rtl" so it
    #    shapes and joins correctly. --
    cta_font = vazirmatn(24, "Bold") if rtl else montserrat(28, "SemiBold")
    icon_space = 56
    pill_pad_x, pill_h = 34, 74
    # Vazirmatn has no glyph for "->"-style arrows, so the Persian pill
    # skips the arrow rather than reserve blank space for a missing glyph.
    cta_full = cta_text if rtl else f"{cta_text}   →"
    cta_w = _text_len(draw, cta_full, cta_font, rtl)
    pill_w = cta_w + 2 * pill_pad_x + icon_space
    pill_x0 = (CANVAS_W - pill_w) / 2
    pill_y0 = min(CANVAS_H - 130, take_bottom + 24)
    outline_kwargs = {"outline": t["cta_outline"], "width": 2} if t["cta_outline"] else {}
    draw.rounded_rectangle([pill_x0, pill_y0, pill_x0 + pill_w, pill_y0 + pill_h],
                            radius=pill_h / 2, fill=t["cta_fill"], **outline_kwargs)
    text_y = pill_y0 + (pill_h - 34) / 2
    if rtl:
        icon_cx = pill_x0 + pill_w - pill_pad_x - 16
        draw_icon("person_plus", draw, icon_cx, pill_y0 + pill_h / 2, 20, t["cta_text"])
        _draw_text(draw, (icon_cx - icon_space - cta_w, text_y), cta_full, cta_font, t["cta_text"], rtl)
    else:
        icon_cx = pill_x0 + pill_pad_x + 16
        draw_icon("person_plus", draw, icon_cx, pill_y0 + pill_h / 2, 20, t["cta_text"])
        draw.text((pill_x0 + pill_pad_x + icon_space, text_y), cta_full, font=cta_font, fill=t["cta_text"])

    # -- corner micro-taglines --
    micro_font = vazirmatn(16, "Bold") if rtl else montserrat(17, "Regular")
    if corner_left_words:
        text = " / ".join(corner_left_words)
        if rtl:
            draw.text((MARGIN, CANVAS_H - 46), text, font=micro_font, fill=muted, direction="rtl", language="fa")
        else:
            draw_tracked_text(draw, (MARGIN, CANVAS_H - 46), text.upper(), micro_font, muted, tracking=1)
    if corner_right_words:
        text = " / ".join(corner_right_words)
        if rtl:
            tw = _text_len(draw, text, micro_font, rtl)
            draw.text((CANVAS_W - MARGIN - tw, CANVAS_H - 46), text, font=micro_font, fill=muted,
                       direction="rtl", language="fa")
        else:
            draw_tracked_text(draw, (CANVAS_W - MARGIN, CANVAS_H - 46), text.upper(), micro_font, muted,
                               tracking=1, anchor_right=True)

    canvas.convert("RGB").save(output_path, quality=92)
