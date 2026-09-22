"""One-off: today's publish run crashed right after the reel (the
create_comment permission error, now fixed and made non-fatal) before any
of the 5 Stories were published. The story videos are already hosted from
the original generate run -- no re-render needed -- so this just builds a
stories-only manifest.json (same lang, same already-hosted URLs) under a
"-fix" tag and lets the normal daily_post.yml publish mode post them.
Deleted once no longer needed.
"""
import json
import os

import requests

import main as main_mod

ORIGINAL_MANIFEST = "https://github.com/HamedR2000/youtubeviwebot/releases/download/daily-2026-09-22/manifest.json"
FIX_TAG_TODAY = "2026-09-22-fix"


def run() -> None:
    orig = requests.get(ORIGINAL_MANIFEST, timeout=30).json()
    story_items = [i for i in orig["items"] if i["type"] == "story"]
    combined = {"date": orig["date"], "lang": orig.get("lang", "en"), "items": story_items}

    os.makedirs(main_mod.WORKDIR, exist_ok=True)
    manifest_path = os.path.join(main_mod.WORKDIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    manifest_url = main_mod._host(FIX_TAG_TODAY, manifest_path)
    os.remove(manifest_path)

    print(f"Built manifest with {len(story_items)} stories (reel already published, skipped).")
    print("MANIFEST_URL:", manifest_url)


if __name__ == "__main__":
    run()
