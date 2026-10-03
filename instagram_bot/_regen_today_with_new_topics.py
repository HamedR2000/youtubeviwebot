"""One-off script: regenerate today's reel + stories using the newly added
trading-principles story-set topics (see content_bank.py), since the
account owner asked for today's content to use those instead of what an
earlier generate run -- made before the new topics were added -- had
already produced and uploaded.

Uploads under tag `daily-{date}-fix` (not `daily-{date}`) so it doesn't
collide with the asset filenames this morning's original run already
uploaded to the `daily-{date}` release.

Temporary -- delete this file and its workflow (_regen_today_with_new_topics.yml)
once the user has approved and today's publish is done.
"""
import datetime
import json
import os

import main
import state as state_mod
from config import config
from github_host import upload_release_asset


def _host_fix(today: str, path: str) -> str:
    return upload_release_asset(
        repo=config.GITHUB_REPOSITORY,
        token=config.GITHUB_TOKEN,
        tag=f"daily-{today}-fix",
        file_path=path,
    )


def regenerate() -> None:
    os.makedirs(main.WORKDIR, exist_ok=True)
    today_date = datetime.date.today()
    today = today_date.isoformat()
    weekday = today_date.weekday()
    lang = "en" if weekday in main.ENGLISH_WEEKDAYS else "fa"
    st = state_mod.load()

    print(f"[{today}] Regenerating under tag daily-{today}-fix, lang={lang}")

    main._host = _host_fix  # build_*_item() calls main._host internally

    items = [main.build_reel_item(today, st, lang)]
    state_mod.save(st)

    items.extend(main.build_story_items(today, st, lang))
    state_mod.save(st)

    if weekday in main.CAROUSEL_WEEKDAYS:
        items.append(main.build_carousel_item(today, st, lang))
        state_mod.save(st)
    elif weekday in main.FEED_POST_WEEKDAYS:
        items.append(main.build_feed_image_item(today, st, lang))
        state_mod.save(st)

    manifest = {"date": today, "lang": lang, "items": items}
    manifest_path = os.path.join(main.WORKDIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    manifest_url = _host_fix(today, manifest_path)
    os.remove(manifest_path)

    print(f"[{today}] Regenerated {len(items)} item(s).")
    print("MANIFEST_URL:", manifest_url)


if __name__ == "__main__":
    regenerate()
