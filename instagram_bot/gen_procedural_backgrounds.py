"""Generates procedural dark velvet-style background artwork -- warm glow,
dark ground, gold dust, a candlestick-chart motif -- stylistically
consistent with the AI-generated photos in backgrounds/, but with
unlimited variety since nothing here is a fixed photo. Existed because the
handful of real photos alone made daily content repeat too fast at this
posting cadence.

Run as: python gen_procedural_backgrounds.py (from inside instagram_bot/).
Writes new files under backgrounds/ -- add their names to
carousel_backgrounds.BACKGROUNDS to bring them into rotation.
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1600
OUT_DIR = os.path.join(os.path.dirname(__file__), "backgrounds")

# (hue name, base near-black tint, glow color) -- a few distinct moods so
# generated files don't all look like reskins of one image.
MOODS = [
    ("burgundy", (14, 8, 9), (140, 55, 60)),
    ("charcoal-gold", (10, 10, 11), (150, 120, 70)),
    ("deep-emerald", (7, 12, 10), (70, 130, 95)),
    ("midnight-blue", (8, 9, 14), (70, 90, 150)),
    ("espresso", (13, 9, 7), (150, 95, 55)),
    ("plum", (12, 7, 12), (130, 70, 130)),
]


def _fold_layer(rng, w, h, tint):
    """A few large soft-edged ellipses at random angles/positions to fake
    a velvet-drape look -- alternating slightly lighter/darker than the
    base so the canvas doesn't read as a flat, dead color."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for _ in range(rng.randint(5, 8)):
        cx, cy = rng.uniform(-0.2, 1.2) * w, rng.uniform(0.3, 1.3) * h
        rx, ry = rng.uniform(0.5, 1.1) * w, rng.uniform(0.15, 0.35) * h
        delta = rng.randint(-10, 14)
        alpha = rng.randint(18, 40)
        fill = tuple(max(0, min(255, c + delta)) for c in tint) + (alpha,)
        ld.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)
    return layer.filter(ImageFilter.GaussianBlur(60))


def _candlesticks(rng, w, h, color):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    n = rng.randint(16, 24)
    band_x0 = rng.uniform(0.0, 0.15) * w
    band_x1 = w * rng.uniform(1.0, 1.1)
    base_y = h * rng.uniform(0.58, 0.72)
    col_w = (band_x1 - band_x0) / n
    trend = 0
    direction = rng.choice([1, -1])
    for i in range(n):
        trend += direction * rng.uniform(-0.4, 1.5)
        cx = band_x0 + col_w * i + col_w / 2
        body_h = rng.uniform(26, 80)
        wick_h = body_h + rng.uniform(10, 36)
        top = base_y - trend * 7 - body_h / 2
        ld.line([(cx, top - wick_h / 2), (cx, top + wick_h / 2)], fill=color, width=2)
        ld.rectangle([cx - col_w * 0.26, top - body_h / 2, cx + col_w * 0.26, top + body_h / 2],
                      fill=color)
    return layer


def _dust(rng, w, h, color, n=140):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h * 0.7)
        r = rng.uniform(0.6, 2.4)
        a = rng.randint(20, 90)
        ld.ellipse([x - r, y - r, x + r, y + r], fill=color + (a,))
    return layer.filter(ImageFilter.GaussianBlur(0.6))


def build(base, glow_color, seed, out_path):
    rng = random.Random(seed)
    canvas = Image.new("RGBA", (W, H), (*base, 255))

    canvas.alpha_composite(_fold_layer(rng, W, H, base))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gcx = rng.uniform(0.05, 0.35) * W
    gcy = rng.uniform(0.0, 0.3) * H
    gr = rng.uniform(0.55, 0.85) * W
    gd.ellipse([gcx - gr, gcy - gr, gcx + gr, gcy + gr], fill=(*glow_color, rng.randint(35, 60)))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(80)))

    gold = (196, 155, 98)
    canvas.alpha_composite(_candlesticks(rng, W, H, gold + (rng.randint(30, 55),)))
    canvas.alpha_composite(_dust(rng, W, H, glow_color, n=rng.randint(90, 170)))

    # gentle bottom vignette so any text/UI placed low stays readable
    fade_h = int(H * 0.22)
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    for i in range(fade_h):
        y = H - fade_h + i
        vd.line([(0, y), (W, y)], fill=int(120 * (i / fade_h)))
    dark = Image.new("RGBA", (W, H), (2, 2, 3, 255))
    canvas = Image.composite(dark, canvas, vig)

    canvas.convert("RGB").save(out_path, quality=92)
    print("wrote", out_path)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for i, (name, base, glow) in enumerate(MOODS):
        build(base, glow, seed=1000 + i, out_path=os.path.join(OUT_DIR, f"procedural-{name}.jpg"))
