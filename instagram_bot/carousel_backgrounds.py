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

A small second pool (PSYCHOLOGY_BACKGROUNDS) holds images that actually
depict a mind/brain, for the handful of story and carousel topics that are
specifically about trading psychology -- per the account owner's request
that the background photo match the content ("اگر راجب روانشناسی ترید هست
مطلب، یه مغز یا یه المان راجبش باشه"). next_background() picks from it
instead of the general pool when called with a matching topic/carousel_id.
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
    # Batch vetted 2026-09-24: free stock photos/illustrations from
    # Pixabay/Pexels/Unsplash the account owner sourced directly. Screened
    # the same way as the rest of this pool -- the crypto-exchange
    # screenshots (Binance, BitMEX, Bitcoin/CoinMarketCap price charts,
    # ADA/USDT, Chiliz) in that batch were left out as off-topic/risky and
    # are not in this list.
    "trader-tablet-annotations.jpg",
    "candlestick-macro-1.jpg",
    "sunglasses-chart-reflection.jpg",
    "candlestick-green-uptrend.jpg",
    "multi-monitor-desk-setup.jpg",
    "stock-indices-dashboard.jpg",
    "candlestick-macro-2.jpg",
    "candlestick-macro-3.jpg",
    "candlestick-moving-averages.jpg",
    "phone-chart-dollar-bill.jpg",
    "businessman-tablet-fintech.jpg",
    "hand-touch-data-wall.jpg",
    "hand-keyboard-chart-overlay.jpg",
    "running-businessman-chart-illustration.jpg",
    "abstract-candlestick-digits.jpg",
]

# AI-generated images (same burgundy-velvet art direction as the rest of the
# pool) that actually show a brain/mind, for psychology-themed content.
PSYCHOLOGY_BACKGROUNDS = [
    "psychology-golden-brain.jpg",
    "psychology-phrenology-bust.jpg",
]

# Story topics (STORY_SETS / STORY_SETS_FA in content_bank.py) that are
# specifically about trading psychology/emotion, in both languages -- the
# "topic" string on the picked story set is checked against this set.
PSYCHOLOGY_STORY_TOPICS = {
    "AFTER A LOSS", "بعد از یک ضرر",
    "PATIENCE PAYS", "صبر جواب می‌ده",
    "EMOTIONS COST MONEY", "احساسات هزینه داره",
    "FOMO", "ترس از دست دادن فرصت",
    "EMOTIONAL DISCIPLINE", "انضباط احساسی",
    "OVERTRADING", "بیش‌ازحد معامله کردن",
}

# Carousel ids (CAROUSELS / CAROUSELS_FA in carousel_content.py) that are
# specifically about trading psychology/mindset -- same ids in both
# languages, so no separate Persian set is needed.
PSYCHOLOGY_CAROUSEL_IDS = {"after-a-loss", "success-is-what-you-dont-see"}


def next_background(state: dict, topic: str = None, carousel_id: str = None) -> str:
    """Pick the next background. When `topic` (a story set's topic string)
    or `carousel_id` matches a psychology-themed entry, rotate through
    PSYCHOLOGY_BACKGROUNDS instead of the general pool."""
    if (topic and topic in PSYCHOLOGY_STORY_TOPICS) or \
            (carousel_id and carousel_id in PSYCHOLOGY_CAROUSEL_IDS):
        (filename,) = state_mod.next_rotating(PSYCHOLOGY_BACKGROUNDS, state, "psychology_bg_cursor")
        return os.path.join(BACKGROUNDS_DIR, filename)
    (filename,) = state_mod.next_rotating(BACKGROUNDS, state, "carousel_bg_cursor")
    return os.path.join(BACKGROUNDS_DIR, filename)
