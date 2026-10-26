"""Infographic slides for the YouTube-to-Reel pipeline (yt_job.py): turns
the structured summary of a trading video (see yt_jobs/README.md for the
content schema) into designed slides, in two sizes from one layout:

  - 1080x1350 carousel slides (Instagram's 4:5 feed maximum)
  - 1080x1920 Reel frames, with the content block kept inside the area
    Instagram's own Reel UI (caption, buttons) doesn't cover

Slide types: "cover", "point", "summary", "cta". A "point" slide can be
rendered partially revealed (`reveal=k` shows only its first k stages:
title, then each bullet, then the takeaway), which yt_reel.py uses to
build bullets up one at a time in sync with the voiceover. The layout is
always measured with every element present, so revealing more never
shifts what's already on screen.

Reuses theme.py colors, icon_kit.py icons and the bundled fonts, so these
read as the same brand as the daily carousels.
"""
import random

from PIL import Image, ImageDraw, ImageFilter

from icon_kit import ICONS, draw_icon
from text_overlay import montserrat, playfair, vazirmatn
from theme import THEMES, add_sparkle_accents, flat_light_background

W = 1080
CAROUSEL_SIZE = (W, 1350)
REEL_SIZE = (W, 1920)
M = 80  # side margin

# Vertical band the content block is centered in, per canvas height. The
# Reel band stops well above the bottom ~400px Instagram covers with the
# caption and like/comment/share buttons.
CONTENT_BAND = {1350: (170, 1350 - 150), 1920: (250, 1920 - 430)}

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def to_fa_digits(text: str) -> str:
    return str(text).translate(FA_DIGITS)


class _Text:
    """Direction-aware text helpers, so each slide type is written once and
    works for Persian (shaped, right-to-left, right-aligned) and English."""

    def __init__(self, rtl: bool, scale: float = 1.0):
        self.rtl = rtl
        self.scale = scale  # shrinks every font, to fit a dense slide in its band
        self.kw = {"direction": "rtl", "language": "fa"} if rtl else {}

    def font(self, size: int, weight: str = "Regular", serif: bool = False):
        if self.rtl:
            return self.fa(size, weight)
        return playfair(round(size * self.scale), weight) if serif else self.latin(size, weight)

    def latin(self, size: int, weight: str = "Regular"):
        return montserrat(round(size * self.scale), weight)

    def fa(self, size: int, weight: str = "Regular"):
        return vazirmatn(round(size * self.scale), weight)

    def line_h(self, font) -> int:
        return int(font.size * (1.55 if self.rtl else 1.28))

    def num(self, n) -> str:
        return to_fa_digits(n) if self.rtl else str(n)

    def length(self, draw, text, font) -> float:
        return draw.textlength(text, font=font, **self.kw)

    def wrap(self, draw, text, font, max_w) -> list:
        lines = []
        for para in str(text).split("\n"):
            cur = ""
            for word in para.split():
                trial = (cur + " " + word).strip()
                if self.length(draw, trial, font) <= max_w or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = word
            lines.append(cur)
        return lines

    def block_h(self, draw, text, font, max_w) -> int:
        return len(self.wrap(draw, text, font, max_w)) * self.line_h(font)

    def block(self, draw, text, font, x0, x1, y, fill, align="start", show=True) -> int:
        """Wrap `text` between x0..x1 and draw it from y. align: "start"
        (right edge for RTL, left for LTR), "center" or "end". Returns the y
        just below the block; with show=False only measures."""
        lh = self.line_h(font)
        for line in self.wrap(draw, text, font, x1 - x0):
            if show:
                lw = self.length(draw, line, font)
                if align == "center":
                    x = (x0 + x1 - lw) / 2
                elif (align == "start") == self.rtl:
                    x = x1 - lw
                else:
                    x = x0
                draw.text((x, y), line, font=font, fill=fill, **self.kw)
            y += lh
        return y

    def start_x(self, x0, x1, width=0):
        """x of an element `width` wide hugging the reading-start side."""
        return x1 - width if self.rtl else x0


def make_background(size: tuple, theme: str, seed: int = 0) -> Image.Image:
    """Theme background. Dark = near-black with a warm glow, faint
    candlestick band and gold dust; light = theme.py's cream card. Callers
    building several frames of one slide should make this once and reuse it
    (both looks carry random texture)."""
    w, h = size
    if theme == "light":
        return flat_light_background(w, h)

    rng = random.Random(seed)
    canvas = Image.new("RGBA", (w, h), (*THEMES["dark"]["canvas_base"], 255))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for cx, cy, r, col in [(w * 0.85, h * 0.08, w * 0.7, (120, 70, 50, 70)),
                           (w * 0.1, h * 0.92, w * 0.8, (196, 155, 98, 38))]:
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))

    candles = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cd = ImageDraw.Draw(candles)
    n, base_y, level = 28, h * 0.9, 0.0
    col_w = w / n
    for i in range(n):
        level += rng.uniform(-1, 1.5)
        cx = col_w * i + col_w / 2
        body = rng.uniform(26, 80)
        top = base_y - level * 7 - body / 2
        color = (196, 155, 98, 34) if rng.random() < 0.6 else (150, 70, 60, 34)
        cd.line([(cx, top - rng.uniform(8, 30)), (cx, top + body + rng.uniform(8, 30))], fill=color, width=2)
        cd.rectangle([cx - col_w * 0.28, top, cx + col_w * 0.28, top + body], fill=color)
    canvas.alpha_composite(candles)
    add_sparkle_accents(canvas, w, h)
    return canvas


def _panel_colors(theme: str):
    if theme == "light":
        return (255, 255, 255, 170), (150, 106, 46, 90)
    return (255, 255, 255, 16), (196, 155, 98, 70)


def _icon(name: str) -> str:
    return name if name in ICONS else "check"


# -- slide types ------------------------------------------------------------
# Each takes (draw, T, slide, theme, x0, x1, y, shown_stages) and returns
# the y just below what it laid out. `shown_stages` is how many reveal
# stages to actually draw (None = all); see stage_count().

def stage_count(slide: dict) -> int:
    """Reveal stages: cover/summary/cta = 1; point = title + one per bullet
    + one for the highlight/takeaway block if present."""
    if slide.get("type") != "point":
        return 1
    extra = 1 if (slide.get("takeaway") or slide.get("highlight")) else 0
    return 1 + len(slide.get("bullets", [])) + extra


def _cover(draw, T, s, theme, x0, x1, y, shown):
    t = THEMES[theme]
    if s.get("kicker"):
        kf = T.font(30, "Bold")
        kw = T.length(draw, s["kicker"], kf) + 56
        kx = T.start_x(x0, x1, kw)
        draw.rounded_rectangle([kx, y, kx + kw, y + 62], radius=31, outline=t["gold"], width=2)
        draw.text((kx + 28, y + (8 if T.rtl else 14)), s["kicker"], font=kf, fill=t["gold_bright"], **T.kw)
        y += 100

    title = s.get("title", "")
    lines = title if isinstance(title, list) else [[title, "white"]]
    tf = T.font(84 if T.rtl else 88, "Black" if T.rtl else "Bold", serif=True)
    for text, tone in lines:
        y = T.block(draw, text, tf, x0, x1, y, t["heading_accent"] if tone == "gold" else t["heading"])
    y += 18
    lx = T.start_x(x0, x1, 90)
    draw.line([(lx, y), (lx + 90, y)], fill=t["gold"], width=3)
    y += 36

    if s.get("subtitle"):
        y = T.block(draw, s["subtitle"], T.font(38), x0, x1, y, t["body"]) + 30

    chips = s.get("chips", [])
    if chips:
        cf = T.font(30, "SemiBold")
        cx = x1 if T.rtl else x0
        for chip in chips:
            cw = T.length(draw, chip["text"], cf) + 120
            left = cx - cw if T.rtl else cx
            fill, outline = _panel_colors(theme)
            draw.rounded_rectangle([left, y, left + cw, y + 84], radius=42, fill=fill, outline=outline, width=2)
            icx = left + cw - 46 if T.rtl else left + 46
            draw_icon(_icon(chip.get("icon", "check")), draw, icx, y + 42, 24, t["gold_bright"])
            tx = left + 26 if T.rtl else left + 84
            draw.text((tx, y + (18 if T.rtl else 24)), chip["text"], font=cf, fill=t["heading"], **T.kw)
            cx = left - 20 if T.rtl else left + cw + 20
        y += 84 + 40

    if s.get("source"):
        y = T.block(draw, s["source"], T.font(26), x0, x1, y, t["muted"])
    return y


def _point(draw, T, s, theme, x0, x1, y, shown):
    t = THEMES[theme]
    fill, outline = _panel_colors(theme)
    stage = 0

    def visible():
        return shown is None or stage < shown

    # Header: gold number disc + small "tip N of M" label.
    r = 46
    disc_cx = x1 - r if T.rtl else x0 + r
    draw.ellipse([disc_cx - r, y, disc_cx + r, y + 2 * r], fill=t["gold"])
    nf = T.latin(44, "Bold")
    num = f"{s.get('number', ''):0>2}" if str(s.get("number", "")).isdigit() else str(s.get("number", ""))
    num = T.num(num)
    nfont = T.fa(44, "Black") if T.rtl else nf
    nw = draw.textlength(num, font=nfont)
    nb = draw.textbbox((0, 0), num, font=nfont)
    draw.text((disc_cx - nw / 2, y + r - (nb[1] + nb[3]) / 2), num, font=nfont, fill=t["canvas_base"])
    if s.get("label"):
        lf = T.font(30, "SemiBold")
        lw = T.length(draw, s["label"], lf)
        lx = disc_cx - r - 24 - lw if T.rtl else disc_cx + r + 24
        draw.text((lx, y + r - T.line_h(lf) / 2 + (4 if T.rtl else 6)), s["label"], font=lf, fill=t["gold_bright"], **T.kw)
    y += 2 * r + 34

    y = T.block(draw, s.get("title", ""), T.font(62 if T.rtl else 64, "ExtraBold" if T.rtl else "Bold", serif=True),
                x0, x1, y, t["heading"]) + 26
    stage += 1

    bf = T.font(35 if T.rtl else 34, "Medium")
    pad, ir = 28, 32
    text_w = (x1 - x0) - 2 * pad - 2 * ir - 26
    for b in s.get("bullets", []):
        text = b["text"] if isinstance(b, dict) else b
        icon = _icon(b.get("icon", "check")) if isinstance(b, dict) else "check"
        th = T.block_h(draw, text, bf, text_w)
        h = max(2 * ir, th) + 2 * pad
        if visible():
            draw.rounded_rectangle([x0, y, x1, y + h], radius=26, fill=fill, outline=outline, width=2)
            icx = x1 - pad - ir if T.rtl else x0 + pad + ir
            draw_icon(icon, draw, icx, y + pad + ir, ir, t["gold_bright"])
            tx0 = x0 + pad if T.rtl else x0 + pad + 2 * ir + 26
            tx1 = x1 - pad - 2 * ir - 26 if T.rtl else x1 - pad
            T.block(draw, text, bf, tx0, tx1, y + pad + max(0, (2 * ir - th) / 2) - (2 if T.rtl else -2),
                    t["heading"])
        y += h + 20
        stage += 1

    hl, take = s.get("highlight"), s.get("takeaway")
    if hl or take:
        y += 14
        show = visible()
        if hl:
            vf = T.latin(92, "ExtraBold") if not T.rtl or str(hl["value"]).isascii() else T.fa(88, "Black")
            value = str(hl["value"])
            vw = draw.textlength(value, font=vf)
            lf = T.font(30)
            lh = T.block_h(draw, hl.get("label", ""), lf, x1 - x0 - 80)
            box_h = 130 + lh + 40
            if show:
                draw.rounded_rectangle([x0, y, x1, y + box_h], radius=30, outline=t["gold"], width=3)
                draw.text(((x0 + x1 - vw) / 2, y + 22), value, font=vf, fill=t["gold_bright"])
                T.block(draw, hl.get("label", ""), lf, x0 + 40, x1 - 40, y + 140, t["body"], align="center")
            y += box_h + 20
        if take:
            tf = T.font(33, "Bold")
            tw = (x1 - x0) - 2 * pad - 2 * 26 - 24
            th = T.block_h(draw, take, tf, tw)
            h = max(52, th) + 2 * pad
            if show:
                draw.rounded_rectangle([x0, y, x1, y + h], radius=26, fill=(*t["gold"], 40 if theme == "dark" else 55),
                                        outline=t["gold"], width=2)
                icx = x1 - pad - 26 if T.rtl else x0 + pad + 26
                draw_icon("bulb", draw, icx, y + h / 2, 26, t["gold_bright"])
                tx0 = x0 + pad if T.rtl else x0 + pad + 76
                tx1 = x1 - pad - 76 if T.rtl else x1 - pad
                T.block(draw, take, tf, tx0, tx1, y + (h - th) / 2 - (2 if T.rtl else -2), t["heading"])
            y += h
    return y


def _summary(draw, T, s, theme, x0, x1, y, shown):
    t = THEMES[theme]
    fill, outline = _panel_colors(theme)
    y = T.block(draw, s.get("title", ""), T.font(64, "ExtraBold" if T.rtl else "Bold", serif=True),
                x0, x1, y, t["heading"]) + 30
    f = T.font(32 if T.rtl else 31, "Medium")
    ir = 24
    for i, item in enumerate(s.get("items", []), 1):
        tw = (x1 - x0) - 2 * 24 - 2 * ir - 70
        th = T.block_h(draw, item, f, tw)
        h = max(2 * ir, th) + 36
        draw.rounded_rectangle([x0, y, x1, y + h], radius=22, fill=fill, outline=outline, width=1)
        nf = T.fa(30, "Black") if T.rtl else T.latin(30, "Bold")
        n = T.num(i)
        nw = draw.textlength(n, font=nf)
        ncx = x1 - 24 - 20 if T.rtl else x0 + 24 + 20
        nb = draw.textbbox((0, 0), n, font=nf)
        draw.text((ncx - nw / 2, y + h / 2 - (nb[1] + nb[3]) / 2), n, font=nf, fill=t["gold_bright"])
        icx = x0 + 24 + ir if T.rtl else x1 - 24 - ir
        draw_icon("check", draw, icx, y + h / 2, ir, t["gold"])
        tx0 = x0 + 24 + 2 * ir + 20 if T.rtl else x0 + 24 + 50
        tx1 = x1 - 24 - 50 if T.rtl else x1 - 24 - 2 * ir - 20
        T.block(draw, item, f, tx0, tx1, y + (h - th) / 2 - (2 if T.rtl else -2), t["heading"])
        y += h + 14
    return y


def _cta(draw, T, s, theme, x0, x1, y, shown):
    t = THEMES[theme]
    y = T.block(draw, s.get("title", ""), T.font(76 if T.rtl else 80, "Black" if T.rtl else "Bold", serif=True),
                x0, x1, y, t["heading"], align="center") + 20
    if s.get("text"):
        y = T.block(draw, s["text"], T.font(36), x0 + 20, x1 - 20, y, t["body"], align="center") + 40

    actions = s.get("actions", [])
    if actions:
        col_w = (x1 - x0) / len(actions)
        af = T.font(28, "SemiBold")
        order = list(reversed(actions)) if T.rtl else actions
        for i, a in enumerate(order):
            cx = x0 + col_w * i + col_w / 2
            draw_icon(_icon(a.get("icon", "check")), draw, cx, y + 44, 44, t["gold_bright"])
            aw = T.length(draw, a["text"], af)
            draw.text((cx - aw / 2, y + 108), a["text"], font=af, fill=t["heading"], **T.kw)
        y += 180

    if s.get("handle"):
        hf = T.latin(36, "Bold")
        hw = draw.textlength(s["handle"], font=hf) + 90
        hx = (x0 + x1 - hw) / 2
        draw.rounded_rectangle([hx, y, hx + hw, y + 80], radius=40, fill=t["cta_fill"],
                                outline=t["cta_outline"], width=2)
        draw.text((hx + 45, y + 18), s["handle"], font=hf, fill=t["cta_text"])
        y += 120
    if s.get("note"):
        y = T.block(draw, s["note"], T.font(24), x0, x1, y, t["muted"], align="center")
    return y


_RENDERERS = {"cover": _cover, "point": _point, "summary": _summary, "cta": _cta}


def render_slide(slide: dict, page: int, total: int, size: tuple, theme: str = "dark",
                 rtl: bool = True, brand: str = "", category: str = "",
                 reveal: int = None, background: Image.Image = None,
                 numbering: bool = True) -> Image.Image:
    """Render one slide to an RGB image. `reveal` limits a point slide to
    its first N stages (None = everything). numbering=False drops every
    "N of M" marker -- the page counter, page dots and a point's "tip N of
    M" label -- which the account owner wants on carousel slides but not
    in the Reel."""
    if not numbering:
        slide = dict(slide, label="")
    w, h = size
    t = THEMES[theme]
    T = _Text(rtl)
    canvas = (background or make_background(size, theme, seed=page)).copy()
    draw = ImageDraw.Draw(canvas)

    # Chrome: category label (reading-start side), page counter (other side),
    # brand handle + page dots at the bottom of the content band.
    top = 70 if h == 1350 else 140
    cf = T.font(26, "Bold") if rtl else montserrat(24, "SemiBold")
    if category:
        clw = T.length(draw, category, cf)
        draw.text((W - M - clw if rtl else M, top), category, font=cf, fill=t["muted"], **T.kw)
    if numbering:
        pf = montserrat(26, "Bold")
        counter = f"{page}/{total}"
        pw = draw.textlength(counter, font=pf)
        px = M if rtl else W - M - pw
        draw.rounded_rectangle([px - 18, top - 6, px + pw + 18, top + 42], radius=24, outline=t["gold"], width=2)
        draw.text((px, top + 1), counter, font=pf, fill=t["heading"])

    band_top, band_bottom = CONTENT_BAND[h]
    footer_y = band_bottom + 40
    if brand:
        bf = montserrat(26, "SemiBold")
        bw = draw.textlength(brand, font=bf)
        draw.text(((W - bw) / 2, footer_y + 30), brand, font=bf, fill=t["gold"])
    dx = (W - (24 * total - 10 + 20)) / 2
    for i in range(total if numbering else 0):
        idx = total - 1 - i if rtl else i
        dw = 34 if idx == page - 1 else 14
        draw.rounded_rectangle([dx, footer_y, dx + dw, footer_y + 14], radius=7,
                                fill=t["gold_bright"] if dw == 34 else (*t["muted"], 90))
        dx += dw + 10

    # Content: draw on its own layer (which also measures its height),
    # shrinking the fonts step by step if it doesn't fit the band, then
    # paste it vertically centered. The fit is decided on the fully
    # revealed slide so every reveal stage uses the same scale.
    render = _RENDERERS[slide.get("type", "point")]
    band = band_bottom - band_top
    for scale in (1.0, 0.92, 0.85, 0.78, 0.72):
        T = _Text(rtl, scale)
        probe = Image.new("RGBA", (w, h * 2), (0, 0, 0, 0))
        if render(ImageDraw.Draw(probe), T, slide, theme, M, W - M, 0, None) <= band:
            break
    else:
        print(f"[yt_infographic] warning: slide {page} still overflows at {w}x{h} -- shorten its text")
    layer = Image.new("RGBA", (w, h * 2), (0, 0, 0, 0))
    used = int(render(ImageDraw.Draw(layer), T, slide, theme, M, W - M, 0, reveal))
    offset = band_top + max(0, (band - used) // 2)
    canvas.alpha_composite(layer.crop((0, 0, w, h - offset)), (0, offset))
    return canvas.convert("RGB")
