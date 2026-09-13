"""One-off: re-render today's 5 Stories with the newly-enriched light theme
background (theme.py), hosted under a separate "-fix" release tag so the
uploads don't collide with this morning's already-hosted assets. Keeps
today's already-approved Reel untouched. Deleted once no longer needed --
see instagram_bot/README.md's note on the generate/publish two-step flow.

Run as: python instagram_bot/_fix_today_stories.py (from repo root, in CI
where the repo secrets are available).
"""
import datetime
import json
import os

import state as state_mod
import main as main_mod

FIX_SUFFIX = "-fix"


def _fixed_host(today: str, path: str):
    return main_mod._host(today + FIX_SUFFIX, path)


def run() -> None:
    os.makedirs(main_mod.WORKDIR, exist_ok=True)
    today_date = datetime.date.today()
    today = today_date.isoformat()
    lang = "en" if today_date.weekday() in main_mod.ENGLISH_WEEKDAYS else "fa"
    st = state_mod.load()

    print(f"[{today}] Re-rendering Stories only, lang={lang}, tag=daily-{today}{FIX_SUFFIX}")

    # Patch the module-level _host so build_story_items' internal calls
    # upload under the "-fix" tag instead of colliding with this morning's
    # already-hosted assets for the same date.
    main_mod._host = _fixed_host

    items = main_mod.build_story_items(today, st, lang)
    state_mod.save(st)

    manifest_path = os.path.join(main_mod.WORKDIR, "stories_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"date": today, "items": items}, f, indent=2, ensure_ascii=False)
    manifest_url = _fixed_host(today, manifest_path)
    os.remove(manifest_path)

    print(f"[{today}] Re-rendered {len(items)} stories.")
    print("STORIES_MANIFEST_URL:", manifest_url)
    for item in items:
        print("STORY_URL:", item["image_url"])


if __name__ == "__main__":
    run()
