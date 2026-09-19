"""One-off: today's stories used the FA "بعد از یک ضرر" set; the account
owner liked stories 1-3 but said the last two lines read as meaningless.
Those lines were just fixed in content_bank.STORY_SETS_FA. This re-renders
ONLY stories 4 and 5 of that same set (same topic, same page numbering)
under a separate "-fix" release tag, leaving the reel and the first 3
already-approved stories untouched. Deleted once no longer needed.
"""
import datetime
import json
import os

import state as state_mod
import main as main_mod
from content_bank import STORY_SETS_FA
from image_composer import build_story_card
from carousel_backgrounds import next_background
from video_composer import compose_story_video

FIX_SUFFIX = "-fix"
_ORIG_HOST = main_mod._host  # captured before monkeypatching, to avoid self-recursion


def _fixed_host(today: str, path: str):
    return _ORIG_HOST(today + FIX_SUFFIX, path)


def run() -> None:
    os.makedirs(main_mod.WORKDIR, exist_ok=True)
    today_date = datetime.date.today()
    today = today_date.isoformat()
    st = state_mod.load()

    story_set = next(s for s in STORY_SETS_FA if s["topic"] == "بعد از یک ضرر")
    lines = story_set["lines"]
    topic = story_set["topic"]
    total = len(lines)

    print(f"[{today}] Re-rendering stories 4-5/{total} of '{topic}', tag=daily-{today}{FIX_SUFFIX}")

    main_mod._host = _fixed_host

    items = []
    for i in (3, 4):
        line = lines[i]
        (theme,) = state_mod.next_rotating(main_mod.THEME_ORDER, st, "story_theme_cursor")
        photo_path = next_background(st) if theme == "dark" else None

        card_path = os.path.join(main_mod.WORKDIR, f"story_{today}_{i}.jpg")
        build_story_card(photo_path, line, main_mod.BRAND_HANDLE, card_path, rtl=True,
                          theme=theme, topic=topic, page_num=i + 1, page_total=total)

        video_path = os.path.join(main_mod.WORKDIR, f"story_{today}_{i}.mp4")
        compose_story_video(card_path, main_mod.MUSIC_DIR, video_path)
        video_url = _fixed_host(today, video_path)

        os.remove(card_path)
        os.remove(video_path)
        items.append({"type": "story", "video_url": video_url})

    state_mod.save(st)

    manifest_path = os.path.join(main_mod.WORKDIR, "stories_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({"date": today, "items": items}, f, indent=2, ensure_ascii=False)
    manifest_url = _fixed_host(today, manifest_path)
    os.remove(manifest_path)

    print(f"[{today}] Re-rendered {len(items)} stories.")
    print("STORIES_MANIFEST_URL:", manifest_url)
    for item in items:
        print("STORY_URL:", item["video_url"])


if __name__ == "__main__":
    run()
