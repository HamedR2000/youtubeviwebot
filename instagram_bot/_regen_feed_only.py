"""One-off script: today's feed-image hook wrapped back to HOOKS_FA[0], a
line the account owner felt was repetitive. Rebuilds ONLY the feed_image
item (next hook/tip/cta in rotation, fresh theme), keeps the already-
approved reel + stories unchanged, and republishes the manifest under a
'-fix' release tag (the original daily-{date} tag already has assets
under these exact filenames, so a plain re-upload would 422). Not part
of the daily pipeline -- run once, then deleted.
"""
import json
import os

import requests

import main as m
import state as state_mod

TODAY = "2026-10-07"
WORKDIR = m.WORKDIR
FIX_TAG = f"daily-{TODAY}-fix"
ORIGINAL_MANIFEST_URL = f"https://github.com/HamedR2000/youtubeviwebot/releases/download/daily-{TODAY}/manifest.json"


def _host_fix(today, path):
    from config import config
    from github_host import upload_release_asset
    return upload_release_asset(
        repo=config.GITHUB_REPOSITORY,
        token=config.GITHUB_TOKEN,
        tag=FIX_TAG,
        file_path=path,
    )


m._host = _host_fix


def main():
    os.makedirs(WORKDIR, exist_ok=True)

    original = requests.get(ORIGINAL_MANIFEST_URL, timeout=30).json()
    kept_items = [item for item in original["items"] if item["type"] != "feed_image"]

    st = state_mod.load()
    new_feed_item = m.build_feed_image_item(TODAY, st, lang="fa")
    state_mod.save(st)

    manifest = {"date": TODAY, "lang": "fa", "items": kept_items + [new_feed_item]}
    manifest_path = os.path.join(WORKDIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    manifest_url = _host_fix(TODAY, manifest_path)
    os.remove(manifest_path)

    print("NEW_FEED_IMAGE_URL:", new_feed_item["image_url"])
    print("NEW_FEED_CAPTION:", new_feed_item["caption"])
    print("MANIFEST_URL:", manifest_url)


if __name__ == "__main__":
    main()
