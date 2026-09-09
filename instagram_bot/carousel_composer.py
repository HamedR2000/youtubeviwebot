"""Renders one slide of a premium dark/gold educational carousel, matching
the reference template style: top category tag + page counter with
progress dashes, decorative micro-taglines, a two-tone headline, a body
paragraph, up to 3 numbered "card" panels with circled line-icons, a
takeaway line, and a bottom CTA pill.

Uses Montserrat (body/UI) + Playfair Display (occasional serif headline
accent) -- both bundled under fonts/ as OFL-licensed variable fonts -- and
icon_kit.py for the circled line icons. No external image assets.
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

from icon_kit import draw_icon

CANVAS_W, CANVAS_H = 1080, 1350
MARGIN = 70

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_MONTSERRAT = os.path.join(FONT_DIR, "Montserrat[wght].ttf")
_PLAYFAIR = os.path.join(FONT_DIR, "PlayfairDisplay[wght].ttf")

WHITE = (240, 241, 243, 255)
GRAY = (156, 163, 175, 255)
GOLD = (205, 164, 92, 255)
GOLD_BRIGHT = (226, 192, 128, 255)
CYAN = (94, 211, 205, 255)
PANEL_BG = (12, 20, 24, 195)
DIM_DASH = (255, 255, 255, 70)


def _font(path, size, variation=None):
    f = ImageFont.truetype(path, size)
    if variation:
        try:
            f.set_variation_by_name(variation)
        except Exception:
            pass
    return f


def montserrat(size, weight="Regular"):
    return _font(_MONTSERRAT, size, weight)


def playfair(size, weight="Bold"):
    return _font(_PLAYFAIR, size, weight)


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


def _wrap_draw(draw, text, font, x, y, max_width_px, fill, line_spacing=10):
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
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y


def _cover_crop(img, w, h):
    scale = max(w / img.width, h / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)))
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def _background(photo_path):
    bg = _cover_crop(Image.open(photo_path).convert("RGB"), CANVAS_W, CANVAS_H).convert("RGBA")
    overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (5, 6, 8, 165))
    canvas = Image.alpha_composite(bg, overlay)

    vignette = Image.new("L", (CANVAS_W, CANVAS_H), 0)
    vd = ImageDraw.Draw(vignette)
    vd.rectangle([0, 0, CANVAS_W, 260], fill=90)
    vd.rectangle([0, CANVAS_H - 320, CANVAS_W, CANVAS_H], fill=110)
    dark = Image.new("RGBA", (CANVAS_W, CANVAS_H), (2, 3, 4, 255))
    canvas = Image.composite(dark, canvas, vignette)
    return canvas


def build_slide(
    photo_path: str,
    output_path: str,
    category_label: str,
    page_num: int,
    page_total: int,
    headline_lines: list,       # [(text, "white"|"gold"), ...] max ~2 lines
    body_text: str,
    panels: list,               # [(icon_name, title, desc), ...] up to 3
    takeaway_text: str,
    cta_text: str,
    top_left_tagline: tuple = None,   # (line1, line2)
    top_right_words: list = None,     # small stacked words, e.g. ["SAME","MARKETS"]
    corner_left_words: list = None,   # e.g. ["ANALYZE","PLAN","EXECUTE"]
    corner_right_words: list = None,  # e.g. ["GOLD","DISCIPLINE","FREEDOM"]
) -> None:
    canvas = _background(photo_path)
    draw = ImageDraw.Draw(canvas)

    # -- top row: category tag (left) + page counter with dashes (right) --
    cat_font = montserrat(28, "SemiBold")
    draw_tracked_text(draw, (MARGIN, 52), category_label.upper(), cat_font, WHITE, tracking=2)

    counter_font = montserrat(34, "Bold")
    counter_text = f"{page_num}/{page_total}"
    counter_w = draw.textlength(counter_text, font=counter_font)
    draw.text((CANVAS_W - MARGIN - counter_w, 44), counter_text, font=counter_font, fill=WHITE)

    dash_w, dash_h, dash_gap = 20, 3, 8
    total_dash_w = page_total * dash_w + (page_total - 1) * dash_gap
    dx = CANVAS_W - MARGIN - total_dash_w
    for i in range(page_total):
        color = CYAN if (i + 1) == page_num else DIM_DASH
        draw.rectangle([dx, 92, dx + dash_w, 92 + dash_h], fill=color)
        dx += dash_w + dash_gap

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

    # -- headline --
    head_font = montserrat(72, "ExtraBold")
    hy = 300
    for text, tone in headline_lines:
        color = GOLD_BRIGHT if tone == "gold" else WHITE
        draw.text((MARGIN, hy), text, font=head_font, fill=color)
        bbox = draw.textbbox((0, 0), text, font=head_font)
        hy += (bbox[3] - bbox[1]) + 14

    # -- body paragraph --
    body_font = montserrat(33, "Regular")
    body_w = CANVAS_W - 2 * MARGIN
    by = _wrap_draw(draw, body_text, body_font, MARGIN, hy + 26, body_w, (201, 205, 211, 255), line_spacing=10)

    # -- numbered panels --
    panel_top = by + 36
    panel_h = 130
    panel_gap = 18
    for idx, (icon_name, title, desc) in enumerate(panels):
        y0 = panel_top + idx * (panel_h + panel_gap)
        y1 = y0 + panel_h
        rrect = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rrect)
        rd.rounded_rectangle([MARGIN, y0, CANVAS_W - MARGIN, y1], radius=22, fill=PANEL_BG)
        canvas.alpha_composite(rrect)
        draw = ImageDraw.Draw(canvas)

        icon_cx, icon_cy, icon_r = MARGIN + 70, (y0 + y1) // 2, 32
        draw_icon(icon_name, draw, icon_cx, icon_cy, icon_r, GOLD)

        title_font = montserrat(32, "Bold")
        desc_font = montserrat(26, "Regular")
        num_font = montserrat(23, "Regular")

        text_x = MARGIN + 138
        draw.text((text_x, y0 + 20), title, font=title_font, fill=WHITE)
        num_text = f"0{idx + 1}"
        num_w = draw.textlength(num_text, font=num_font)
        draw.text((CANVAS_W - MARGIN - 24 - num_w, y0 + 24), num_text, font=num_font, fill=GRAY)
        _wrap_draw(draw, desc, desc_font, text_x, y0 + 66, CANVAS_W - MARGIN - 24 - text_x, GRAY, line_spacing=4)

    # -- takeaway line --
    panels_bottom = panel_top + len(panels) * (panel_h + panel_gap) - (panel_gap if panels else 0)
    take_font = montserrat(34, "SemiBold")
    ty = panels_bottom + (34 if panels else 20)
    take_bottom = _wrap_draw(draw, takeaway_text, take_font, MARGIN, ty, CANVAS_W - 2 * MARGIN, WHITE, line_spacing=6)

    # -- bottom CTA pill --
    cta_font = montserrat(28, "SemiBold")
    cta_full = f"{cta_text}  →"
    cta_w = draw.textlength(cta_full, font=cta_font)
    pill_pad_x, pill_h = 36, 70
    pill_w = cta_w + 2 * pill_pad_x
    pill_x0 = (CANVAS_W - pill_w) / 2
    pill_y0 = min(CANVAS_H - 128, take_bottom + 26)
    draw.rounded_rectangle([pill_x0, pill_y0, pill_x0 + pill_w, pill_y0 + pill_h],
                            radius=pill_h / 2, outline=CYAN, width=2)
    draw.text((pill_x0 + pill_pad_x, pill_y0 + (pill_h - 34) / 2), cta_full, font=cta_font, fill=WHITE)

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
