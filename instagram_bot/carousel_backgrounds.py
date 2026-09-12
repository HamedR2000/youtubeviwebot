"""Bank of dark-theme background images for carousel slides, stories and
feed cards -- used instead of a live Pexels search so everything shares
one consistent art direction. Three kinds, interleaved so the rotation
doesn't run through one kind before the other:

- AI-generated photos (burgundy velvet + luxury object) the account owner
  supplied, matching their reference style.
- Procedurally generated velvet/glow + candlestick-motif artwork
  (gen_procedural_backgrounds.py), added because the 7 photos alone made
  content repeat too fast at this posting cadence -- these cost nothing
  to add more of and never look identical twice if regenerated, though
  they're a plainer fallback than the real photos.
- Vetted stock photos (Unsplash/Pixabay/Pexels) of generic charts, desks
  and devices -- no visible broker/exchange/platform branding, no
  legible real portfolio or personal account details, and not crypto
  (off-topic for a gold/forex account). Photos with any of that were
  screened out rather than added here.

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
    "blogging-guide-K5DY18hy5JQ-unsplash.jpg",
    "geralt-dollar-rate-544949_1920.jpg",
    "pexels-jakubzerdzicki-35501928.jpg",
    "nimisha-mekala-fchVIvuMGBI-unsplash.jpg",
    "pexels-kampus-8353831.jpg",
    "pix1861-a-book-602631_1920.jpg",
    "anne-nygard-x07ELaNFt34-unsplash.jpg",
    "pix1861-chart-840333_1920.jpg",
    "spectra112-trading-8799817_1920.png",
    "sergeitokmakov-stock-trading-6525081_1920.jpg",
    "pexels-thales13-38343508.jpg",
    "theinvestorpost-man-5782415_1920.jpg",
]


def next_background(state: dict) -> str:
    (filename,) = state_mod.next_rotating(BACKGROUNDS, state, "carousel_bg_cursor")
    return os.path.join(BACKGROUNDS_DIR, filename)
