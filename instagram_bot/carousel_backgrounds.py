"""Bank of dark-theme background images for carousel slides, stories and
feed cards -- used instead of a live Pexels search so everything shares
one consistent art direction. Two kinds, interleaved so the rotation
doesn't run through one kind before the other:

- AI-generated photos (burgundy velvet + luxury object) the account owner
  supplied, matching their reference style.
- Procedurally generated velvet/glow + candlestick-motif artwork
  (gen_procedural_backgrounds.py), added because the 7 photos alone made
  content repeat too fast at this posting cadence -- these cost nothing
  to add more of and never look identical twice if regenerated, though
  they're a plainer fallback than the real photos.

Add more files to backgrounds/ and list them here to keep growing the
pool; state.carousel_bg_cursor rotates through them so the same one isn't
reused back-to-back.
"""
import os

import state as state_mod

BACKGROUNDS_DIR = os.path.join(os.path.dirname(__file__), "backgrounds")

BACKGROUNDS = [
    "magnifier-coins.png",
    "procedural-burgundy.jpg",
    "pocket-watch-chart-1.jpg",
    "procedural-charcoal-gold.jpg",
    "fountain-pen-1.jpg",
    "procedural-deep-emerald.jpg",
    "pocket-watch-chart-2.jpg",
    "procedural-midnight-blue.jpg",
    "fountain-pen-2.jpg",
    "procedural-espresso.jpg",
    "pocket-watch-chart-3.jpg",
    "procedural-plum.jpg",
    "fountain-pen-3.jpg",
    "pinterest-desk-skyline.jpg",
]


def next_background(state: dict) -> str:
    (filename,) = state_mod.next_rotating(BACKGROUNDS, state, "carousel_bg_cursor")
    return os.path.join(BACKGROUNDS_DIR, filename)
