"""One-off: re-render today's 3 stories again now that the story font/
palette was also fixed to match the carousel (see PR that added this
comment). Hosts under a fresh tag + corrected manifest.json. Not part of
the ongoing pipeline -- delete after use.
"""
import datetime
import json
import os

from carousel_backgrounds import next_background
from github_host import upload_release_asset
from image_composer import build_story_card
import state as state_mod

GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REEL_URL = os.environ["REEL_URL"]
REEL_CAPTION = os.environ["REEL_CAPTION"]

TODAY = datetime.date.today().isoformat()
LINES = [
    "DXY up, gold down. Usually.",
    "The trend is your friend -- until it bends.",
    "Automate the boring part. Telegram in bio.",
]
OUT_DIR = os.path.join(os.path.dirname(__file__), "_fix_output")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    tag = f"daily-{TODAY}-fix2"

    st = state_mod.load()
    story_urls = []
    for i, line in enumerate(LINES):
        photo_path = next_background(st)
        out_path = os.path.join(OUT_DIR, f"story_{i}.jpg")
        build_story_card(photo_path, line, "@Goldhamedsignals", out_path)
        url = upload_release_asset(GITHUB_REPOSITORY, GITHUB_TOKEN, tag, out_path)
        print(f"Story {i}: {photo_path} -> {url}")
        story_urls.append(url)

    manifest = {
        "date": TODAY,
        "items": [
            {"type": "reel", "video_url": REEL_URL, "caption": REEL_CAPTION},
            *[{"type": "story", "image_url": u} for u in story_urls],
        ],
    }
    manifest_path = os.path.join(OUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    manifest_url = upload_release_asset(GITHUB_REPOSITORY, GITHUB_TOKEN, tag, manifest_path)
    print("MANIFEST_URL:", manifest_url)


if __name__ == "__main__":
    main()
