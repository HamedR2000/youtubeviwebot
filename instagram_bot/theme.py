"""Shared color themes + the flat cream background generator, used by
carousel_composer.py and image_composer.py so a "light" post (cream/gold,
no photo) and a "dark" post (near-black + a hero photo) both read as the
same design system, just two moods -- per the account owner's feedback
that everything read too uniformly dark.
"""
import random

from PIL import Image, ImageDraw

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
    """Warm cream canvas with a soft off-center glow and a faint bottom
    warm shade for depth -- the light theme has no photo, unlike dark's
    hero-photo background, so this keeps it from reading flat/dead."""
    base = THEMES["light"]["canvas_base"]
    canvas = Image.new("RGBA", (w, h), (*base, 255))

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gcx, gcy, gr = int(w * 0.72), int(h * 0.2), int(w * 0.85)
    gd.ellipse([gcx - gr, gcy - gr, gcx + gr, gcy + gr], fill=(255, 250, 240, 70))
    canvas.alpha_composite(glow)

    fade_h = int(h * 0.24)
    vignette = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vignette)
    for i in range(fade_h):
        y = h - fade_h + i
        a = int(38 * (i / fade_h))
        vd.line([(0, y), (w, y)], fill=a)
    warm_edge = Image.new("RGBA", (w, h), (222, 210, 190, 255))
    canvas = Image.composite(warm_edge, canvas, vignette)

    _draw_faint_candlesticks(canvas, w, h)
    return canvas


def _draw_faint_candlesticks(canvas: Image.Image, w: int, h: int) -> None:
    """A soft, low-opacity candlestick chart along the lower-right, so a
    light-themed slide with little text doesn't read as empty -- same
    quiet-texture role the hero photo plays on the dark theme, without
    competing with the foreground text."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    rng = random.Random(42)  # fixed seed: identical decoration on every render
    n = 22
    band_x0, band_x1 = int(w * 0.38), int(w * 1.05)
    base_y = int(h * 0.86)
    col_w = (band_x1 - band_x0) / n
    trend = 0
    color = (150, 106, 46, 26)
    for i in range(n):
        trend += rng.uniform(-1, 1.6)
        cx = band_x0 + col_w * i + col_w / 2
        body_h = rng.uniform(30, 90)
        wick_h = body_h + rng.uniform(10, 40)
        top = base_y - trend * 6 - body_h / 2
        ld.line([(cx, top - wick_h / 2), (cx, top + body_h / 2 + wick_h / 2 - body_h)],
                fill=color, width=2)
        ld.rectangle([cx - col_w * 0.28, top - body_h / 2, cx + col_w * 0.28, top + body_h / 2],
                      fill=color)
    canvas.alpha_composite(layer)
