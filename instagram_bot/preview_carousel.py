"""Standalone script used only by .github/workflows/preview_carousel_test.yml
to render one full 3-slide carousel topic (real background photos + real
content) and publish each slide as a GitHub Release asset, so it can be
reviewed before the full daily pipeline integration is built. Not part of
the daily posting pipeline. (Uses a Release instead of an Actions artifact
because Actions artifacts are served from a blob-storage host the
reviewing agent cannot reach; Release assets are served from github.com's
own domain.)
"""
import datetime
import os
import random

from carousel_backgrounds import next_background
from carousel_composer import build_slide
from carousel_content import BRAND_CORNER_LEFT, BRAND_CORNER_RIGHT, CAROUSELS
from github_host import upload_release_asset
import state as state_mod

GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
OUT_DIR = os.path.join(os.path.dirname(__file__), "_preview_output")

TOPIC_ID = os.environ.get("PREVIEW_TOPIC_ID")  # optional override


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    topic = next((t for t in CAROUSELS if t["id"] == TOPIC_ID), None) or random.choice(CAROUSELS)
    print(f"Topic: {topic['id']}")

    st = state_mod.load()
    tag = "carousel-preview-" + datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    urls = []

    for i, slide in enumerate(topic["slides"]):
        page_num = i + 1
        page_total = len(topic["slides"])

        photo_path = next_background(st)

        output_path = os.path.join(OUT_DIR, f"slide_{page_num}of{page_total}.jpg")
        build_slide(
            photo_path=photo_path,
            output_path=output_path,
            category_label=topic["category"],
            page_num=page_num,
            page_total=page_total,
            headline_lines=slide["headline_lines"],
            body_text=slide["body_text"],
            panels=slide["panels"],
            takeaway_text=slide["takeaway_text"],
            cta_text=slide["cta_text"],
            top_left_tagline=slide.get("top_left_tagline"),
            top_right_words=slide.get("top_right_words"),
            corner_left_words=BRAND_CORNER_LEFT,
            corner_right_words=BRAND_CORNER_RIGHT,
        )
        print(f"Rendered slide {page_num}/{page_total}")

        url = upload_release_asset(GITHUB_REPOSITORY, GITHUB_TOKEN, tag, output_path)
        print(f"Uploaded slide {page_num}: {url}")
        urls.append(url)

    print("ALL_URLS:", " ".join(urls))


if __name__ == "__main__":
    main()
