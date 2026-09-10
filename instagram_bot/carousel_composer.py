"""Renders one slide of a premium dark/gold-copper educational carousel,
matching the account owner's reference template: top category tag + a
plain circled page counter, decorative micro-taglines, a two-tone serif
headline, a body paragraph, a 3-column row of circled line-icons (label +
short caption, divided by thin rules), a shadowed takeaway line, and a
bottom CTA pill with a small icon.

Uses Montserrat (UI/body) + Playfair Display (serif headline) -- both
bundled under fonts/ as OFL-licensed variable fonts -- and icon_kit.py for
the circled line icons. No external image assets.
"""
from PIL import Image, ImageDraw

from icon_kit import draw_icon
from text_overlay import draw_wrapped_px, montserrat, playfair, wrap_lines_px

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 70

CREAM = (240, 235, 225, 255)
WHITE = (235, 231, 224, 255)
GRAY = (176, 172, 166, 255)
GOLD = (196, 155, 98, 255)
GOLD_BRIGHT = (214, 175, 116, 255)
SHADOW = (0, 0, 0, 170)


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
               align="left", shadow=False):
    return draw_wrapped_px(draw, text, font, x, y, max_width_px, fill,
                            line_spacing=line_spacing, align=align,
                            shadow=SHADOW if shadow else None)


def _cover_crop(img, w, h):
    scale = max(w / img.width, h / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)))
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


HERO_H = 620          # height of the photo region, anchored to the bottom
HERO_FEATHER = 220    # how tall the fade-to-dark transition at its top edge is


def _background(photo_path):
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
) -> None:
    canvas = _background(photo_path)
    draw = ImageDraw.Draw(canvas)

    # -- top row: category tag (left) + plain circled page counter (right) --
    cat_font = montserrat(28, "SemiBold")
    draw_tracked_text(draw, (MARGIN, 52), category_label.upper(), cat_font, CREAM, tracking=2)

    counter_font = montserrat(30, "Bold")
    counter_text = f"{page_num}/{page_total}"
    r = 44
    ccx, ccy = CANVAS_W - MARGIN - r, 50 + r
    draw.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], outline=CREAM, width=2)
    cw = draw.textlength(counter_text, font=counter_font)
    bbox = draw.textbbox((0, 0), counter_text, font=counter_font)
    draw.text((ccx - cw / 2, ccy - (bbox[3] - bbox[1]) / 2 - bbox[1]), counter_text,
               font=counter_font, fill=CREAM)

    # -- decorative micro-taglines --
    tag_font = montserrat(20, "Regular")
    if top_left_tagline:
        draw.line([(MARGIN, 130), (MARGIN + 34, 130)], fill=GOLD, width=2)
        ty = 140
        for line in top_left_tagline:
            draw_tracked_text(draw, (MARGIN, ty), line.upper(), tag_font, GRAY, tracking=2)
            ty += 26

    if top_right_words:
        ty = 140
        for w in top_right_words:
            draw_tracked_text(draw, (CANVAS_W - MARGIN, ty), w.upper(), tag_font, GRAY,
                               tracking=2, anchor_right=True)
            ty += 26

    # -- headline: serif, two-tone, word-wrapped so long phrases never spill
    #    off the canvas edge --
    head_font = playfair(70, "Bold")
    headline_max_w = CANVAS_W - 2 * MARGIN
    hy = 300
    for text, tone in headline_lines:
        color = GOLD_BRIGHT if tone == "gold" else CREAM
        for pl in _wrap_lines(draw, text, head_font, headline_max_w):
            draw.text((MARGIN, hy), pl, font=head_font, fill=color)
            bbox = draw.textbbox((0, 0), pl, font=head_font)
            hy += (bbox[3] - bbox[1]) + 16

    hy += 14
    draw.line([(MARGIN, hy), (MARGIN + 60, hy)], fill=GOLD, width=2)
    hy += 26

    # -- body paragraph --
    body_font = montserrat(33, "Regular")
    body_w = CANVAS_W - 2 * MARGIN
    by = _wrap_draw(draw, body_text, body_font, MARGIN, hy, body_w, (206, 202, 196, 255), line_spacing=10)

    # -- 3-column icon row: circled icon, bold label, short caption, thin
    #    vertical dividers between columns. Everything gets a soft drop
    #    shadow since this section can sit over the hero photo. --
    panel_top = by + 46
    n = max(len(panels), 1)
    col_w = (CANVAS_W - 2 * MARGIN) / n
    icon_r = 34
    label_font = montserrat(30, "Bold")
    desc_font = montserrat(23, "Regular")
    col_bottom = panel_top

    for idx, (icon_name, title, desc) in enumerate(panels):
        col_cx = MARGIN + col_w * idx + col_w / 2
        icon_cy = panel_top + icon_r + 4

        shadow_disc = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow_disc)
        sd.ellipse([col_cx - icon_r - 8, icon_cy - icon_r - 8, col_cx + icon_r + 8, icon_cy + icon_r + 8],
                   fill=(0, 0, 0, 110))
        canvas.alpha_composite(shadow_disc)
        draw = ImageDraw.Draw(canvas)
        draw_icon(icon_name, draw, col_cx, icon_cy, icon_r, GOLD_BRIGHT)

        label_y = icon_cy + icon_r + 22
        label_w = draw.textlength(title, font=label_font)
        draw.text((col_cx - label_w / 2 + 1, label_y + 1), title, font=label_font, fill=SHADOW)
        draw.text((col_cx - label_w / 2, label_y), title, font=label_font, fill=CREAM)
        bbox = draw.textbbox((0, 0), title, font=label_font)
        desc_y = label_y + (bbox[3] - bbox[1]) + 10

        desc_bottom = _wrap_draw(draw, desc, desc_font, col_cx, desc_y, col_w - 28, GRAY,
                                  line_spacing=6, align="center", shadow=True)
        col_bottom = max(col_bottom, desc_bottom)

        if idx > 0:
            div_x = MARGIN + col_w * idx
            draw.line([(div_x, panel_top + 4), (div_x, col_bottom - 6)], fill=(*GOLD[:3], 90), width=1)

    # -- takeaway line: short gold divider, then shadowed centered text --
    take_y = col_bottom + 34
    draw.line([(CANVAS_W / 2 - 30, take_y), (CANVAS_W / 2 + 30, take_y)], fill=GOLD, width=2)
    take_y += 20
    take_font = montserrat(32, "SemiBold")
    take_bottom = _wrap_draw(draw, takeaway_text, take_font, CANVAS_W / 2, take_y,
                              CANVAS_W - 2 * MARGIN - 60, CREAM, line_spacing=8,
                              align="center", shadow=True)

    # -- bottom CTA pill (centered, outlined, small icon + text + arrow) --
    cta_font = montserrat(28, "SemiBold")
    cta_full = f"{cta_text}   →"
    cta_w = draw.textlength(cta_full, font=cta_font)
    icon_space = 56
    pill_pad_x, pill_h = 34, 74
    pill_w = cta_w + 2 * pill_pad_x + icon_space
    pill_x0 = (CANVAS_W - pill_w) / 2
    pill_y0 = min(CANVAS_H - 130, take_bottom + 24)
    draw.rounded_rectangle([pill_x0, pill_y0, pill_x0 + pill_w, pill_y0 + pill_h],
                            radius=pill_h / 2, fill=(8, 6, 6, 190), outline=GOLD, width=2)
    icon_cx = pill_x0 + pill_pad_x + 16
    draw_icon("person_plus", draw, icon_cx, pill_y0 + pill_h / 2, 20, GOLD_BRIGHT)
    draw.text((pill_x0 + pill_pad_x + icon_space, pill_y0 + (pill_h - 34) / 2), cta_full,
               font=cta_font, fill=CREAM)

    # -- corner micro-taglines --
    micro_font = montserrat(17, "Regular")
    if corner_left_words:
        draw_tracked_text(draw, (MARGIN, CANVAS_H - 46), " / ".join(corner_left_words).upper(),
                           micro_font, GRAY, tracking=1)
    if corner_right_words:
        text = " / ".join(corner_right_words).upper()
        draw_tracked_text(draw, (CANVAS_W - MARGIN, CANVAS_H - 46), text, micro_font, GRAY,
                           tracking=1, anchor_right=True)

    canvas.convert("RGB").save(output_path, quality=92)
