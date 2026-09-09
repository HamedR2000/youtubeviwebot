"""Minimal hand-drawn line-icon set (Pillow primitives only, no icon font or
image assets) used inside the circled icon badges on carousel slides.
Each icon_* function draws within a circle of radius r centered at (cx, cy).
"""
import math


def _ring(draw, cx, cy, r, color, width=3):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)


def icon_trend_up(draw, cx, cy, r, color, width=5):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.5
    pts = [(cx - s, cy + s * 0.5), (cx - s * 0.15, cy - s * 0.1), (cx + s * 0.35, cy + s * 0.3), (cx + s, cy - s * 0.6)]
    draw.line(pts, fill=color, width=width, joint="curve")
    ah = s * 0.35
    draw.line([(cx + s - ah, cy - s * 0.6), (cx + s, cy - s * 0.6)], fill=color, width=width)
    draw.line([(cx + s, cy - s * 0.6), (cx + s, cy - s * 0.6 + ah)], fill=color, width=width)


def icon_shield(draw, cx, cy, r, color, width=5):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.55
    top = cy - s
    pts = [(cx, top), (cx + s, top + s * 0.4), (cx + s, top + s * 1.2),
           (cx, top + s * 2.1), (cx - s, top + s * 1.2), (cx - s, top + s * 0.4)]
    draw.line(pts + [pts[0]], fill=color, width=width, joint="curve")
    draw.line([(cx - s * 0.4, top + s * 1.1), (cx - s * 0.05, top + s * 1.5), (cx + s * 0.5, top + s * 0.7)],
               fill=color, width=width, joint="curve")


def icon_globe(draw, cx, cy, r, color, width=4):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.55
    draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=width)
    draw.ellipse([cx - s * 0.45, cy - s, cx + s * 0.45, cy + s], outline=color, width=width)
    draw.line([(cx - s, cy), (cx + s, cy)], fill=color, width=width)


def icon_coins(draw, cx, cy, r, color, width=4):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.5
    draw.ellipse([cx - s, cy - s * 0.3, cx + s, cy + s * 0.5], outline=color, width=width)
    draw.ellipse([cx - s * 0.75, cy - s * 0.7, cx + s * 0.75, cy + s * 0.1], outline=color, width=width)


def icon_search(draw, cx, cy, r, color, width=5):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.45
    lx, ly = cx - s * 0.15, cy - s * 0.15
    draw.ellipse([lx - s, ly - s, lx + s, ly + s], outline=color, width=width)
    draw.line([(lx + s * 0.7, ly + s * 0.7), (cx + s * 0.9, cy + s * 0.9)], fill=color, width=width)


def icon_document(draw, cx, cy, r, color, width=4):
    _ring(draw, cx, cy, r, color, width)
    w, h = r * 0.7, r * 0.9
    x0, y0 = cx - w / 2, cy - h / 2
    draw.rectangle([x0, y0, x0 + w, y0 + h], outline=color, width=width)
    for i in range(3):
        y = y0 + h * 0.28 + i * h * 0.22
        draw.line([(x0 + w * 0.18, y), (x0 + w * 0.82, y)], fill=color, width=max(2, width - 1))


def icon_gear(draw, cx, cy, r, color, width=4):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.5
    draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=width)
    draw.ellipse([cx - s * 0.3, cy - s * 0.3, cx + s * 0.3, cy + s * 0.3], outline=color, width=width)
    for i in range(8):
        a = i * math.pi / 4
        x1, y1 = cx + s * math.cos(a), cy + s * math.sin(a)
        x2, y2 = cx + s * 1.3 * math.cos(a), cy + s * 1.3 * math.sin(a)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=width)


def icon_bar_chart(draw, cx, cy, r, color, width=5):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.55
    base = cy + s
    bars = [(-s * 0.7, s * 0.4), (-s * 0.1, -s * 0.2), (s * 0.5, -s * 0.9)]
    for dx, top in bars:
        draw.line([(cx + dx, base), (cx + dx, cy + top)], fill=color, width=width * 2)


def icon_clock(draw, cx, cy, r, color, width=4):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.55
    draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=width)
    draw.line([(cx, cy), (cx, cy - s * 0.65)], fill=color, width=width)
    draw.line([(cx, cy), (cx + s * 0.45, cy + s * 0.1)], fill=color, width=width)


def icon_target(draw, cx, cy, r, color, width=4):
    _ring(draw, cx, cy, r, color, width)
    for s in (r * 0.6, r * 0.35, r * 0.12):
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=width)


def icon_scale(draw, cx, cy, r, color, width=4):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.55
    draw.line([(cx, cy - s), (cx, cy + s * 0.6)], fill=color, width=width)
    draw.line([(cx - s, cy - s * 0.4), (cx + s, cy - s * 0.4)], fill=color, width=width)
    for dx in (-s, s):
        draw.arc([cx + dx - s * 0.35, cy - s * 0.4, cx + dx + s * 0.35, cy - s * 0.4 + s * 0.5],
                  0, 180, fill=color, width=width)
    draw.line([(cx - s * 0.5, cy + s * 0.6), (cx + s * 0.5, cy + s * 0.6)], fill=color, width=width)


def icon_arrows_swap(draw, cx, cy, r, color, width=5):
    _ring(draw, cx, cy, r, color, width)
    s = r * 0.5
    draw.line([(cx - s, cy - s * 0.3), (cx + s, cy - s * 0.3)], fill=color, width=width)
    draw.line([(cx + s * 0.6, cy - s * 0.7), (cx + s, cy - s * 0.3), (cx + s * 0.6, cy + s * 0.1)],
              fill=color, width=width, joint="curve")
    draw.line([(cx + s, cy + s * 0.3), (cx - s, cy + s * 0.3)], fill=color, width=width)
    draw.line([(cx - s * 0.6, cy - s * 0.1), (cx - s, cy + s * 0.3), (cx - s * 0.6, cy + s * 0.7)],
              fill=color, width=width, joint="curve")


ICONS = {
    "trend_up": icon_trend_up,
    "shield": icon_shield,
    "globe": icon_globe,
    "coins": icon_coins,
    "search": icon_search,
    "document": icon_document,
    "gear": icon_gear,
    "bar_chart": icon_bar_chart,
    "clock": icon_clock,
    "target": icon_target,
    "scale": icon_scale,
    "arrows_swap": icon_arrows_swap,
}


def draw_icon(name, draw, cx, cy, r, color):
    ICONS[name](draw, cx, cy, r, color)
