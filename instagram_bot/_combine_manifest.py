"""One-off: combine this morning's already-approved Reel + first 3 Stories
(from the original daily-2026-09-19 manifest) with the 2 re-rendered
Stories (from the daily-2026-09-19-fix stories_manifest, see
_fix_two_stories.py) into one manifest.json, hosted under the same "-fix"
release tag, so the normal daily_post.yml publish mode can be used
unchanged. Deleted once no longer needed.
"""
import json
import os

import requests

import main as main_mod

ORIGINAL_MANIFEST = "https://github.com/HamedR2000/youtubeviwebot/releases/download/daily-2026-09-19/manifest.json"
FIX_STORIES_MANIFEST = "https://github.com/HamedR2000/youtubeviwebot/releases/download/daily-2026-09-19-fix/stories_manifest.json"
FIX_TAG_TODAY = "2026-09-19-fix"


def run() -> None:
    orig = requests.get(ORIGINAL_MANIFEST, timeout=30).json()
    fix = requests.get(FIX_STORIES_MANIFEST, timeout=30).json()

    reel_item = next(i for i in orig["items"] if i["type"] == "reel")
    original_stories = [i for i in orig["items"] if i["type"] == "story"][:3]
    combined = {"date": orig["date"], "items": [reel_item] + original_stories + fix["items"]}

    os.makedirs(main_mod.WORKDIR, exist_ok=True)
    manifest_path = os.path.join(main_mod.WORKDIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    manifest_url = main_mod._host(FIX_TAG_TODAY, manifest_path)
    os.remove(manifest_path)

    print(f"Combined {len(combined['items'])} items (1 reel + {len(original_stories)} original "
          f"stories + {len(fix['items'])} re-rendered stories).")
    print("MANIFEST_URL:", manifest_url)


if __name__ == "__main__":
    run()
