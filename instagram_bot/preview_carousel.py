"""Standalone script used only by .github/workflows/preview_carousel_test.yml
to render ONE real carousel slide (real Pexels photo + real content) and
publish it as a GitHub Release asset, so it can be reviewed before the full
content bank / daily pipeline integration is built. Not part of the daily
posting pipeline. (Uses a Release instead of an Actions artifact because
Actions artifacts are served from a blob-storage host the reviewing agent
cannot reach; Release assets are served from github.com's own domain.)
"""
import datetime
import os
import random

import requests

from carousel_composer import build_slide
from github_host import upload_release_asset

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OUT_DIR = os.path.join(os.path.dirname(__file__), "_preview_output")


def fetch_photo(query: str, dest_path: str) -> None:
    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": 15},
        timeout=30,
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    if not photos:
        raise RuntimeError(f"No Pexels photos found for query: {query}")
    photo = random.choice(photos)
    img_url = photo["src"]["large2x"]
    img_resp = requests.get(img_url, timeout=60)
    img_resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(img_resp.content)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    photo_path = os.path.join(OUT_DIR, "hero_photo.jpg")
    fetch_photo("gold bars", photo_path)

    build_slide(
        photo_path=photo_path,
        output_path=os.path.join(OUT_DIR, "slide_1of5.jpg"),
        category_label="XAUUSD | GOLD TRADING",
        page_num=1,
        page_total=5,
        headline_lines=[("SMART TRADING", "white"), ("STARTS BEFORE THE ENTRY", "gold")],
        body_text="Before you enter any gold trade, check the bigger trend, key levels, and market structure. Good entries are prepared, not guessed.",
        panels=[
            ("trend_up", "Trend", "Follow the bigger picture"),
            ("bar_chart", "Key Levels", "Find opportunities at key zones"),
            ("target", "Structure", "Understand the market flow"),
        ],
        takeaway_text="Better analysis, a brighter tomorrow.",
        cta_text="Follow for daily XAUUSD insights",
        top_left_tagline=("PLAN", "ANALYZE"),
        top_right_words=["BETTER", "ANALYSIS", "A BRIGHTER", "TOMORROW"],
        corner_left_words=["PLAN", "ANALYZE", "TRADE", "GROW"],
        corner_right_words=["GOLD", "DISCIPLINE", "PATIENCE", "FREEDOM"],
    )
    output_path = os.path.join(OUT_DIR, "slide_1of5.jpg")
    print("Rendered", output_path)

    tag = "carousel-preview-" + datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    url = upload_release_asset(GITHUB_REPOSITORY, GITHUB_TOKEN, tag, output_path)
    print("Uploaded to:", url)


if __name__ == "__main__":
    main()
