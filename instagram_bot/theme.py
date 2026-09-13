"""Shared color themes + the flat cream background generator, used by
carousel_composer.py and image_composer.py so a "light" post (cream/gold,
no photo) and a "dark" post (near-black + a hero photo) both read as the
same design system, just two moods -- per the account owner's feedback
that everything read too uniformly dark.
"""
import random

from PIL import Image, ImageDraw, ImageFilter

THEMES = {
    "dark": {
        "canvas_base": (10, 8, 9),
        "heading": (240, 235, 225),
        "heading_accent": (214, 175, 116),
        "body": (206, 202, 196),
        "muted": (176, 172, 166),
        "gold": (196, 155, 98),
        "gold_bright": (214, 175, 116),
        "shadow": (0, 0, 0, 170),
        "cta_fill": (8, 6, 6, 190),
        "cta_outline": (196, 155, 98, 255),
        "cta_text": (240, 235, 225, 255),
        "counter_style": "ring",
    },
    "light": {
        "canvas_base": (246, 240, 229),
        "heading": (32, 28, 23),
        "heading_accent": (150, 106, 46),
        "body": (82, 75, 64),
        "muted": (140, 132, 118),
        "gold": (150, 106, 46),
        "gold_bright": (132, 92, 38),
        "shadow": (0, 0, 0, 35),
        "cta_fill": (24, 20, 16, 255),
        "cta_outline": None,
        "cta_text": (240, 235, 225, 255),
        "counter_style": "pill",
    },
}


def flat_light_background(w: int, h: int) -> Image.Image:
    """Warm cream canvas, layered up with a richer set of decorative
    elements -- two warm glows, a full-width candlestick band, scattered
    gold dust with a few brighter twinkles, and a thin ornamental frame --
    so the light theme reads as a designed, glamorous card rather than an
    empty page (the account owner's own words: "شلوغتر و پر زرق و برق‌تر",
    busier and more glamorous, after the first plain version)."""
    base = THEMES["light"]["canvas_base"]
    canvas = Image.new("RGBA", (w, h), (*base, 255))

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gcx, gcy, gr = int(w * 0.78), int(h * 0.14), int(w * 0.95)
    gd.ellipse([gcx - gr, gcy - gr, gcx + gr, gcy + gr], fill=(255, 250, 235, 110))
    gcx2, gcy2, gr2 = int(w * 0.08), int(h * 0.9), int(w * 0.75)
    gd.ellipse([gcx2 - gr2, gcy2 - gr2, gcx2 + gr2, gcy2 + gr2], fill=(214, 175, 116, 60))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))

    _draw_rich_candlesticks(canvas, w, h)
    _draw_gold_dust(canvas, w, h)
    _draw_ornamental_frame(canvas, w, h)

    fade_h = int(h * 0.24)
    vignette = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vignette)
    for i in range(fade_h):
        y = h - fade_h + i
        a = int(38 * (i / fade_h))
        vd.line([(0, y), (w, y)], fill=a)
    warm_edge = Image.new("RGBA", (w, h), (222, 210, 190, 255))
    canvas = Image.composite(warm_edge, canvas, vignette)

    return canvas


def _draw_rich_candlesticks(canvas: Image.Image, w: int, h: int) -> None:
    """A wider, more visible candlestick chart spanning most of the width,
    low in the frame -- reads as "trading chart" texture without competing
    with foreground text, but fuller than a single faint corner sliver."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    rng = random.Random()  # unseeded: a different candle pattern every render
    n = 32
    band_x0, band_x1 = int(w * -0.05), int(w * 1.05)
    base_y = int(h * rng.uniform(0.78, 0.88))
    col_w = (band_x1 - band_x0) / n
    trend = 0
    color = (150, 106, 46, 46)
    for i in range(n):
        trend += rng.uniform(-1, 1.6)
        cx = band_x0 + col_w * i + col_w / 2
        body_h = rng.uniform(30, 100)
        wick_h = body_h + rng.uniform(10, 46)
        top = base_y - trend * 6 - body_h / 2
        ld.line([(cx, top - wick_h / 2), (cx, top + body_h / 2 + wick_h / 2 - body_h)],
                fill=color, width=2)
        ld.rectangle([cx - col_w * 0.3, top - body_h / 2, cx + col_w * 0.3, top + body_h / 2],
                      fill=color)
    canvas.alpha_composite(layer)


def _draw_gold_dust(canvas: Image.Image, w: int, h: int) -> None:
    """Scattered gold particles across the whole canvas, plus a handful of
    brighter 4-point twinkle marks, for the "پر زرق و برق" (glittery,
    glamorous) look -- the dark theme's photo backgrounds already have
    plenty going on visually, the light theme's flat cream needed this to
    not read as bare."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    rng = random.Random()
    gold = (150, 106, 46)
    for _ in range(220):
        x, y = rng.uniform(0, w), rng.uniform(0, h * 0.92)
        r = rng.uniform(0.8, 3.2)
        a = rng.randint(25, 90)
        ld.ellipse([x - r, y - r, x + r, y + r], fill=gold + (a,))

    for _ in range(10):
        x, y = rng.uniform(w * 0.05, w * 0.95), rng.uniform(h * 0.05, h * 0.88)
        size = rng.uniform(7, 14)
        a = rng.randint(90, 160)
        color = (214, 175, 116, a)
        ld.line([(x - size, y), (x + size, y)], fill=color, width=1)
        ld.line([(x, y - size), (x, y + size)], fill=color, width=1)
        small = size * 0.4
        ld.line([(x - small, y - small), (x + small, y + small)], fill=color, width=1)
        ld.line([(x - small, y + small), (x + small, y - small)], fill=color, width=1)

    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(0.4)))


def _draw_ornamental_frame(canvas: Image.Image, w: int, h: int) -> None:
    """A thin double gold rule inset from the edges with small diamond
    accents at the corners -- gives the light theme the "framed, designed
    card" feel the dark theme gets for free from its hero photo."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    gold = (150, 106, 46, 100)
    inset1, inset2 = 34, 42
    ld.rectangle([inset1, inset1, w - inset1, h - inset1], outline=gold, width=1)
    ld.rectangle([inset2, inset2, w - inset2, h - inset2], outline=gold, width=1)

    d = 9
    for cx, cy in [(inset1, inset1), (w - inset1, inset1), (inset1, h - inset1), (w - inset1, h - inset1)]:
        ld.polygon([(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)],
                    outline=(150, 106, 46, 160), width=1)

    canvas.alpha_composite(layer)
