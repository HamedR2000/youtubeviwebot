"""One-off: re-render today's (2026-09-25) 3-slide carousel with the dark
(hero photo) theme instead of light (flat cream) -- the account owner said
the light theme's carousel background is "too repetitive", and today's
new backgrounds/ photo pool gives dark-theme carousels real visual variety
for the first time. Re-packages the already-approved reel + 5 stories
(unchanged, already hosted) alongside the newly rendered carousel images
into a fresh manifest under a "-fix" tag. See README.md for the
established one-off-script pattern this follows.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import state as state_mod
from carousel_backgrounds import next_background
from carousel_composer import build_slide
from carousel_content import BRAND_CORNER_LEFT, BRAND_CORNER_RIGHT, CAROUSELS
from config import config
from github_host import upload_release_asset

TODAY = "2026-09-25"
FIX_TAG = f"daily-{TODAY}-fix"
WORKDIR = os.path.join(os.path.dirname(__file__), "_build")

# Already-hosted, unchanged from the original approved manifest.
REEL_URL = f"https://github.com/{config.GITHUB_REPOSITORY}/releases/download/daily-{TODAY}/reel_{TODAY}.mp4"
REEL_CAPTION = (
    "Gold rewards patience more than it rewards speed.\n\n"
    "A missed trade costs you nothing. A bad trade can cost you weeks.\n\n"
    "Want your gold trades executed with zero emotion? Join the Telegram channel in my bio -- "
    "6-month & 1-year access available.\n\n"
    "⚠️ Educational content only, not financial advice. Trading gold/forex carries a high "
    "level of risk and may not be suitable for everyone. Past performance does not guarantee "
    "future results.\n\n"
    "#goldhamedsignals #investing #financialfreedom #priceaction #technicalanalysis "
    "#tradingsignals #forexsignals #goldprice #preciousmetals #wallstreet #tradertips "
    "#tradingstrategy #algotrading #fintech #tradinglife #forexmarket #goldinvestment "
    "#tradereducation #usdollar #marketanalysis #automatedtrading"
)
STORY_URLS = [
    f"https://github.com/{config.GITHUB_REPOSITORY}/releases/download/daily-{TODAY}/story_{TODAY}_{i}.mp4"
    for i in range(5)
]


def main():
    os.makedirs(WORKDIR, exist_ok=True)
    st = state_mod.load()

    topic = next(t for t in CAROUSELS if t["id"] == "protect-your-capital")
    theme = "dark"
    print(f"[{TODAY}] Re-rendering carousel '{topic['id']}' with theme={theme}")

    image_urls = []
    for i, slide in enumerate(topic["slides"]):
        page_num, page_total = i + 1, len(topic["slides"])
        photo_path = next_background(st)

        output_path = os.path.join(WORKDIR, f"carousel_{TODAY}_{page_num}_fix.jpg")
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
            theme=theme,
            rtl=False,
        )
        url = upload_release_asset(
            repo=config.GITHUB_REPOSITORY, token=config.GITHUB_TOKEN, tag=FIX_TAG, file_path=output_path,
        )
        image_urls.append(url)
        os.remove(output_path)
        print(f"[{TODAY}] Slide {page_num}/{page_total}: {url}")

    state_mod.save(st)

    carousel_caption = (
        "PROTECT YOUR CAPITAL\n\n"
        "Define your risk before you enter, keep position size reasonable, and aim for at least 1:2 reward.\n\n"
        "Telegram in bio for full access\n\n"
        "⚠️ Educational content only, not financial advice. Trading gold/forex carries a high "
        "level of risk and may not be suitable for everyone. Past performance does not guarantee "
        "future results.\n\n"
        "#goldhamedsignals #gold #goldtrading #xauusd #forex #forextrading #trading #tradingbot "
        "#daytrading #swingtrading #stockmarket #investing #financialfreedom #priceaction "
        "#technicalanalysis #tradingsignals #forexsignals #goldprice #preciousmetals #wallstreet #tradertips"
    )

    manifest = {
        "date": TODAY,
        "lang": "en",
        "items": [
            {"type": "reel", "video_url": REEL_URL, "caption": REEL_CAPTION},
            *[{"type": "story", "video_url": u} for u in STORY_URLS],
            {"type": "carousel", "image_urls": image_urls, "caption": carousel_caption},
        ],
    }
    manifest_path = os.path.join(WORKDIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    manifest_url = upload_release_asset(
        repo=config.GITHUB_REPOSITORY, token=config.GITHUB_TOKEN, tag=FIX_TAG, file_path=manifest_path,
    )
    print(f"MANIFEST_URL: {manifest_url}")


if __name__ == "__main__":
    main()
