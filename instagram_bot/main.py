"""Daily entry point. Run as: python -m instagram_bot.main
(or `python main.py` from inside instagram_bot/).

Pipeline: pick unused stock clip -> compose Reel with text + music ->
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
from content_bank import CTAS, DISCLAIMER, HOOKS, STOCK_SEARCH_TERMS, TIPS
from github_host import publish_video_as_release_asset
from instagram_publish import publish_reel
from stock_media import download_video, find_unused_video
from video_composer import compose_video

BRAND_HANDLE = "@your_handle"  # TODO: replace with your real Instagram handle
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
WORKDIR = os.path.join(os.path.dirname(__file__), "_build")


def main() -> None:
    os.makedirs(WORKDIR, exist_ok=True)
    today = datetime.date.today().isoformat()

    st = state_mod.load()

    print(f"[{today}] Finding an unused stock clip...")
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

    print(f"[{today}] Composing video (clip #{video_info['id']}, term '{video_info['search_term']}')...")
    output_path = os.path.join(WORKDIR, f"post_{today}.mp4")
    compose_video(
        raw_video_path=raw_path,
        hook=hook,
        tip=tip,
        brand_handle=BRAND_HANDLE,
        music_dir=MUSIC_DIR,
        output_path=output_path,
    )

    caption = build_caption(hook=hook, tip=tip, cta=cta, disclaimer=DISCLAIMER, state=st)
    print(f"[{today}] Caption:\n{caption}\n")

    print(f"[{today}] Uploading rendered video as a GitHub Release asset...")
    video_url = publish_video_as_release_asset(
        repo=config.GITHUB_REPOSITORY,
        token=config.GITHUB_TOKEN,
        tag=f"daily-post-{today}",
        video_path=output_path,
    )
    print(f"[{today}] Public video URL: {video_url}")

    print(f"[{today}] Publishing to Instagram...")
    ig_media_id = publish_reel(
        version=config.GRAPH_API_VERSION,
        ig_user_id=config.IG_USER_ID,
        access_token=config.IG_ACCESS_TOKEN,
        video_url=video_url,
        caption=caption,
    )
    print(f"[{today}] Published! Instagram media id: {ig_media_id}")

    st["used_pexels_ids"].append(video_info["id"])
    st["posts"].append({"date": today, "pexels_id": video_info["id"], "ig_media_id": ig_media_id})
    state_mod.save(st)

    os.remove(raw_path)
    os.remove(output_path)


if __name__ == "__main__":
    main()
