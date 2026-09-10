"""Fixed bank of bespoke AI-generated background photos for carousel slides
(burgundy velvet + luxury object, matching the account owner's reference
style) -- used instead of a live Pexels search so every slide shares one
consistent art direction. Add more files to backgrounds/ and list them here
to grow the pool; state.carousel_bg_cursor rotates through them so the same
one isn't reused back-to-back.
"""
import os

import state as state_mod

BACKGROUNDS_DIR = os.path.join(os.path.dirname(__file__), "backgrounds")

BACKGROUNDS = [
    "magnifier-coins.png",
    "pocket-watch-chart-1.jpg",
    "pocket-watch-chart-2.jpg",
    "pocket-watch-chart-3.jpg",
    "fountain-pen-1.jpg",
    "fountain-pen-2.jpg",
    "fountain-pen-3.jpg",
]


def next_background(state: dict) -> str:
    (filename,) = state_mod.next_rotating(BACKGROUNDS, state, "carousel_bg_cursor")
    return os.path.join(BACKGROUNDS_DIR, filename)
