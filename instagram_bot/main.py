"""Daily entry point. Run as: python main.py (from inside instagram_bot/,
or `python instagram_bot/main.py` from the repo root).

Each run publishes, in order:
  - 1 Reel (always)               -- stock video + text overlay + music
  - N Story cards (always)        -- stock photo + one short line, no caption
  - 1 Feed image post (Mon/Wed/Fri) -- stock photo + hook/tip/CTA card

Pipeline per item: pick unused stock media -> compose with Pillow/moviepy ->
host the file publicly via a GitHub Release -> publish to Instagram ->
persist rotation/dedupe state.
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import state as state_mod
from caption_builder import build_caption
from config import config
from content_bank import CTAS, DISCLAIMER, HOOKS, STOCK_SEARCH_TERMS, STORY_LINES, TIPS
from github_host import upload_release_asset
from image_composer import build_feed_card, build_story_card
from instagram_publish import publish_feed_image, publish_reel, publish_story
from stock_media import download_video, find_unused_video
from stock_photos import download_photo, find_unused_photo
from video_composer import compose_video

BRAND_HANDLE = "@your_handle"  # TODO: replace with your real Instagram handle
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
WORKDIR = os.path.join(os.path.dirname(__file__), "_build")

STORIES_PER_DAY = 3
# Mon=0 ... Sun=6 (datetime.date.weekday()) -- post a feed image 3x/week.
FEED_POST_WEEKDAYS = {0, 2, 4}


def _host(today: str, path: str) -> str:
    return upload_release_asset(
        repo=config.GITHUB_REPOSITORY,
        token=config.GITHUB_TOKEN,
        tag=f"daily-post-{today}",
        file_path=path,
    )


def post_reel(today: str, st: dict) -> None:
    print(f"[{today}] Reel: finding an unused stock clip...")
    video_info = find_unused_video(
        api_key=config.PEXELS_API_KEY,
        search_terms=STOCK_SEARCH_TERMS,
        used_ids=set(st["used_pexels_ids"]),
    )
    raw_path = os.path.join(WORKDIR, f"raw_{video_info['id']}.mp4")
    download_video(video_info["download_url"], raw_path)

    (hook,) = state_mod.next_rotating(HOOKS, st, "hook_cursor")
    (tip,) = state_mod.next_rotating(TIPS, st, "tip_cursor")
    (cta,) = state_mod.next_rotating(CTAS, st, "cta_cursor")

    output_path = os.path.join(WORKDIR, f"reel_{today}.mp4")
    compose_video(raw_video_path=raw_path, hook=hook, tip=tip, brand_handle=BRAND_HANDLE,
                  music_dir=MUSIC_DIR, output_path=output_path)

    caption = build_caption(hook=hook, tip=tip, cta=cta, disclaimer=DISCLAIMER, state=st)
    video_url = _host(today, output_path)
    ig_media_id = publish_reel(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                config.IG_ACCESS_TOKEN, video_url, caption)
    print(f"[{today}] Reel published: {ig_media_id}")

    st["used_pexels_ids"].append(video_info["id"])
    st["posts"].append({"date": today, "type": "reel", "pexels_id": video_info["id"], "ig_media_id": ig_media_id})

    os.remove(raw_path)
    os.remove(output_path)


def post_stories(today: str, st: dict) -> None:
    lines = state_mod.next_rotating(STORY_LINES, st, "story_line_cursor", count=STORIES_PER_DAY)

    for i, line in enumerate(lines):
        print(f"[{today}] Story {i + 1}/{STORIES_PER_DAY}: finding an unused stock photo...")
        photo_info = find_unused_photo(
            api_key=config.PEXELS_API_KEY,
            search_terms=STOCK_SEARCH_TERMS,
            used_ids=set(st["used_pexels_photo_ids"]),
        )
        raw_path = os.path.join(WORKDIR, f"story_raw_{photo_info['id']}.jpg")
        download_photo(photo_info["download_url"], raw_path)

        output_path = os.path.join(WORKDIR, f"story_{today}_{i}.jpg")
        build_story_card(raw_path, line, BRAND_HANDLE, output_path)

        image_url = _host(today, output_path)
        ig_media_id = publish_story(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                     config.IG_ACCESS_TOKEN, image_url=image_url)
        print(f"[{today}] Story published: {ig_media_id}")

        st["used_pexels_photo_ids"].append(photo_info["id"])
        st["posts"].append({"date": today, "type": "story", "pexels_id": photo_info["id"], "ig_media_id": ig_media_id})

        os.remove(raw_path)
        os.remove(output_path)


def post_feed_image(today: str, st: dict) -> None:
    print(f"[{today}] Feed post: finding an unused stock photo...")
    photo_info = find_unused_photo(
        api_key=config.PEXELS_API_KEY,
        search_terms=STOCK_SEARCH_TERMS,
        used_ids=set(st["used_pexels_photo_ids"]),
    )
    raw_path = os.path.join(WORKDIR, f"feed_raw_{photo_info['id']}.jpg")
    download_photo(photo_info["download_url"], raw_path)

    (hook,) = state_mod.next_rotating(HOOKS, st, "hook_cursor")
    (tip,) = state_mod.next_rotating(TIPS, st, "tip_cursor")
    (cta,) = state_mod.next_rotating(CTAS, st, "cta_cursor")

    output_path = os.path.join(WORKDIR, f"feed_{today}.jpg")
    build_feed_card(raw_path, headline=hook, subtitle=tip, cta=cta,
                     brand_handle=BRAND_HANDLE, output_path=output_path)

    caption = build_caption(hook=hook, tip=tip, cta=cta, disclaimer=DISCLAIMER, state=st)
    image_url = _host(today, output_path)
    ig_media_id = publish_feed_image(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                      config.IG_ACCESS_TOKEN, image_url, caption)
    print(f"[{today}] Feed post published: {ig_media_id}")

    st["used_pexels_photo_ids"].append(photo_info["id"])
    st["posts"].append({"date": today, "type": "feed", "pexels_id": photo_info["id"], "ig_media_id": ig_media_id})

    os.remove(raw_path)
    os.remove(output_path)


def main() -> None:
    os.makedirs(WORKDIR, exist_ok=True)
    today_date = datetime.date.today()
    today = today_date.isoformat()

    st = state_mod.load()

    post_reel(today, st)
    state_mod.save(st)  # save after each item so a later failure doesn't lose earlier progress

    post_stories(today, st)
    state_mod.save(st)

    if today_date.weekday() in FEED_POST_WEEKDAYS:
        post_feed_image(today, st)
        state_mod.save(st)
    else:
        print(f"[{today}] Skipping feed post (not a scheduled weekday).")


if __name__ == "__main__":
    main()
