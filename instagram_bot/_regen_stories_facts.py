"""One-off: re-render today's (2026-09-27) 5 stories using the new
"فکت‌های ترید" (TRADE FACTS) set instead of the "سطح‌ها رو بشناس" set the
normal generate run picked -- the account owner didn't like today's
story lines and asked for the new sourced-facts set instead (see the
content_bank.py commit that added it). Re-packages them with the
already-approved, unchanged Reel into a fresh manifest under a "-fix"
tag. See README.md for the established one-off-script pattern this
follows.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import state as state_mod
from carousel_backgrounds import next_background
from config import config
from github_host import upload_release_asset
from image_composer import build_story_card
from video_composer import compose_story_video

TODAY = "2026-09-27"
FIX_TAG = f"daily-{TODAY}-fix"
WORKDIR = os.path.join(os.path.dirname(__file__), "_build")
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
BRAND_HANDLE = "@Goldhamedsignals"
THEME_ORDER = ["dark", "light"]

# Already-hosted, unchanged from the original approved manifest.
REEL_URL = f"https://github.com/{config.GITHUB_REPOSITORY}/releases/download/daily-{TODAY}/reel_{TODAY}.mp4"
REEL_CAPTION = (
    "بازار حرکت کرد. برنامه‌ت هم حرکت کرد؟\n\n"
    "حمایت و مقاومت، ناحیه‌ن نه خط‌های دقیق. به معاملاتت فضای نفس‌کشیدن بده.\n\n"
    "دیگه تمام روز چارت نگاه نکن. بذار ربات برنامه رو معامله کنه، تو زندگیت رو بکن. لینک تو بایو.\n\n"
    "⚠️ این محتوا فقط آموزشیه و مشاوره‌ی مالی نیست. "
    "معامله‌ی طلا/فارکس ریسک بالایی داره و ممکنه برای همه مناسب نباشه. "
    "عملکرد گذشته تضمینی برای نتایج آینده نیست.\n\n"
    "#goldhamedsignals #investing #financialfreedom #priceaction #technicalanalysis "
    "#tradingsignals #forexsignals #goldprice #preciousmetals #wallstreet #tradertips "
    "#tradingstrategy #algotrading #fintech #tradinglife #forexmarket #goldinvestment "
    "#tradereducation #usdollar #marketanalysis #automatedtrading"
)


def main():
    os.makedirs(WORKDIR, exist_ok=True)
    st = state_mod.load()

    import content_bank
    story_set = next(s for s in content_bank.STORY_SETS_FA if s["topic"] == "فکت‌های ترید")
    topic, lines = story_set["topic"], story_set["lines"]

    story_urls = []
    for i, line in enumerate(lines):
        (theme,) = state_mod.next_rotating(THEME_ORDER, st, "story_theme_cursor")
        print(f"[{TODAY}] Story {i + 1}/{len(lines)} ('{topic}'): rendering ({theme})...")
        photo_path = next_background(st) if theme == "dark" else None

        card_path = os.path.join(WORKDIR, f"story_{TODAY}_{i}_fix.jpg")
        build_story_card(photo_path, line, BRAND_HANDLE, card_path, rtl=True, theme=theme,
                          topic=topic, page_num=i + 1, page_total=len(lines))

        video_path = os.path.join(WORKDIR, f"story_{TODAY}_{i}_fix.mp4")
        compose_story_video(card_path, MUSIC_DIR, video_path)
        url = upload_release_asset(
            repo=config.GITHUB_REPOSITORY, token=config.GITHUB_TOKEN, tag=FIX_TAG, file_path=video_path,
        )
        story_urls.append(url)
        os.remove(card_path)
        os.remove(video_path)
        print(f"[{TODAY}] Story {i + 1}/{len(lines)}: {url}")

    state_mod.save(st)

    manifest = {
        "date": TODAY,
        "lang": "fa",
        "items": [
            {"type": "reel", "video_url": REEL_URL, "caption": REEL_CAPTION},
            *[{"type": "story", "video_url": u} for u in story_urls],
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
