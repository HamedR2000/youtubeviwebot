"""Daily entry point, run in one of two modes (env var PIPELINE_MODE):

  generate (default) -- builds today's content (1 Reel, 5 Stories, and
    either a feed image card or a full educational carousel depending on
    the weekday), hosts every asset as a public GitHub Release asset, and
    writes+uploads a manifest.json describing what was built. Does NOT
    call the Instagram API at all -- this is the "show me before it goes
    out" half of the pipeline. Everything posted on a given day is in one
    language -- English on ENGLISH_WEEKDAYS (Mon/Wed/Fri), Persian the
    rest of the week -- see ENGLISH_WEEKDAYS below.

  publish -- takes a manifest URL (env MANIFEST_URL, produced by a prior
    generate run once a human has reviewed and approved it) and actually
    publishes each item to Instagram using the already-hosted assets. No
    regeneration, no new Pexels picks -- what was approved is what posts.

Run as: python main.py (from inside instagram_bot/).
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import requests

import state as state_mod
from caption_builder import build_caption
from carousel_backgrounds import next_background
from carousel_composer import build_slide
from carousel_content import (
    BRAND_CORNER_LEFT,
    BRAND_CORNER_LEFT_FA,
    BRAND_CORNER_RIGHT,
    BRAND_CORNER_RIGHT_FA,
    CAROUSELS,
    CAROUSELS_FA,
)
from config import config
from content_bank import (
    CTAS,
    CTAS_FA,
    DISCLAIMER,
    DISCLAIMER_FA,
    HOOKS,
    HOOKS_FA,
    STOCK_SEARCH_TERMS,
    STORY_LINES,
    STORY_LINES_FA,
    TIPS,
    TIPS_FA,
)
from github_host import upload_release_asset
from image_composer import build_feed_card, build_story_card
from instagram_publish import publish_carousel, publish_feed_image, publish_reel, publish_story
from stock_media import download_video, find_unused_video
from stock_photos import download_photo, find_unused_photo
from video_composer import compose_video

BRAND_HANDLE = "@Goldhamedsignals"
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
WORKDIR = os.path.join(os.path.dirname(__file__), "_build")

STORIES_PER_DAY = 5
# Mon=0 ... Sun=6 (datetime.date.weekday())
FEED_POST_WEEKDAYS = {2}        # Wed: a single feed image card
CAROUSEL_WEEKDAYS = {0, 4}      # Mon, Fri: a full educational carousel
ENGLISH_WEEKDAYS = {0, 2, 4}    # Mon, Wed, Fri: everything posted that day is in English
                                 # (every other day -- Sat, Sun, Tue, Thu -- is Persian)

# Alternates dark (hero photo) and light (flat cream, no photo) so the
# whole account doesn't read as uniformly dark -- each content type keeps
# its own rotation cursor.
THEME_ORDER = ["dark", "light"]

PIPELINE_MODE = os.environ.get("PIPELINE_MODE", "generate")


def _host(today: str, path: str) -> str:
    return upload_release_asset(
        repo=config.GITHUB_REPOSITORY,
        token=config.GITHUB_TOKEN,
        tag=f"daily-{today}",
        file_path=path,
    )


def build_reel_item(today: str, st: dict, lang: str) -> dict:
    print(f"[{today}] Reel: finding an unused stock clip...")
    video_info = find_unused_video(
        api_key=config.PEXELS_API_KEY,
        search_terms=STOCK_SEARCH_TERMS,
        used_ids=set(st["used_pexels_ids"]),
    )
    raw_path = os.path.join(WORKDIR, f"raw_{video_info['id']}.mp4")
    download_video(video_info["download_url"], raw_path)

    rtl = lang == "fa"
    hooks, tips, ctas, disclaimer = (HOOKS_FA, TIPS_FA, CTAS_FA, DISCLAIMER_FA) if rtl \
        else (HOOKS, TIPS, CTAS, DISCLAIMER)
    hook_cursor, tip_cursor, cta_cursor = ("hook_fa_cursor", "tip_fa_cursor", "cta_fa_cursor") if rtl \
        else ("hook_cursor", "tip_cursor", "cta_cursor")
    (hook,) = state_mod.next_rotating(hooks, st, hook_cursor)
    (tip,) = state_mod.next_rotating(tips, st, tip_cursor)
    (cta,) = state_mod.next_rotating(ctas, st, cta_cursor)

    output_path = os.path.join(WORKDIR, f"reel_{today}.mp4")
    compose_video(raw_video_path=raw_path, hook=hook, tip=tip, brand_handle=BRAND_HANDLE,
                  music_dir=MUSIC_DIR, output_path=output_path, rtl=rtl)

    caption = build_caption(hook=hook, tip=tip, cta=cta, disclaimer=disclaimer, state=st)
    video_url = _host(today, output_path)

    st["used_pexels_ids"].append(video_info["id"])
    os.remove(raw_path)
    os.remove(output_path)
    return {"type": "reel", "video_url": video_url, "caption": caption}


def build_story_items(today: str, st: dict, lang: str) -> list:
    rtl = lang == "fa"
    story_lines, cursor_key = (STORY_LINES_FA, "story_line_fa_cursor") if rtl \
        else (STORY_LINES, "story_line_cursor")
    lines = state_mod.next_rotating(story_lines, st, cursor_key, count=STORIES_PER_DAY)

    items = []
    for i, line in enumerate(lines):
        (theme,) = state_mod.next_rotating(THEME_ORDER, st, "story_theme_cursor")
        print(f"[{today}] Story {i + 1}/{STORIES_PER_DAY}: rendering ({theme})...")
        photo_path = next_background(st) if theme == "dark" else None

        output_path = os.path.join(WORKDIR, f"story_{today}_{i}.jpg")
        build_story_card(photo_path, line, BRAND_HANDLE, output_path, rtl=rtl, theme=theme)
        image_url = _host(today, output_path)

        os.remove(output_path)
        items.append({"type": "story", "image_url": image_url})
    return items


def build_feed_image_item(today: str, st: dict, lang: str) -> dict:
    (theme,) = state_mod.next_rotating(THEME_ORDER, st, "feed_theme_cursor")
    print(f"[{today}] Feed post: theme={theme}")

    raw_path = None
    photo_info = None
    if theme == "dark":
        photo_info = find_unused_photo(
            api_key=config.PEXELS_API_KEY,
            search_terms=STOCK_SEARCH_TERMS,
            used_ids=set(st["used_pexels_photo_ids"]),
        )
        raw_path = os.path.join(WORKDIR, f"feed_raw_{photo_info['id']}.jpg")
        download_photo(photo_info["download_url"], raw_path)

    rtl = lang == "fa"
    hooks, tips, ctas, disclaimer = (HOOKS_FA, TIPS_FA, CTAS_FA, DISCLAIMER_FA) if rtl \
        else (HOOKS, TIPS, CTAS, DISCLAIMER)
    hook_cursor, tip_cursor, cta_cursor = ("hook_fa_cursor", "tip_fa_cursor", "cta_fa_cursor") if rtl \
        else ("hook_cursor", "tip_cursor", "cta_cursor")
    (hook,) = state_mod.next_rotating(hooks, st, hook_cursor)
    (tip,) = state_mod.next_rotating(tips, st, tip_cursor)
    (cta,) = state_mod.next_rotating(ctas, st, cta_cursor)

    output_path = os.path.join(WORKDIR, f"feed_{today}.jpg")
    build_feed_card(raw_path, headline=hook, subtitle=tip, cta=cta,
                     brand_handle=BRAND_HANDLE, output_path=output_path, theme=theme, rtl=rtl)
    caption = build_caption(hook=hook, tip=tip, cta=cta, disclaimer=disclaimer, state=st)
    image_url = _host(today, output_path)

    if theme == "dark":
        st["used_pexels_photo_ids"].append(photo_info["id"])
        os.remove(raw_path)
    os.remove(output_path)
    return {"type": "feed_image", "image_url": image_url, "caption": caption}


def build_carousel_item(today: str, st: dict, lang: str) -> dict:
    rtl = lang == "fa"
    carousels, cursor_key = (CAROUSELS_FA, "carousel_topic_fa_cursor") if rtl \
        else (CAROUSELS, "carousel_topic_cursor")
    corner_left = BRAND_CORNER_LEFT_FA if rtl else BRAND_CORNER_LEFT
    corner_right = BRAND_CORNER_RIGHT_FA if rtl else BRAND_CORNER_RIGHT
    disclaimer = DISCLAIMER_FA if rtl else DISCLAIMER

    (topic,) = state_mod.next_rotating(carousels, st, cursor_key)
    (theme,) = state_mod.next_rotating(THEME_ORDER, st, "carousel_theme_cursor")
    print(f"[{today}] Carousel: topic '{topic['id']}' theme={theme} lang={lang}")

    image_urls = []
    for i, slide in enumerate(topic["slides"]):
        page_num, page_total = i + 1, len(topic["slides"])
        photo_path = next_background(st) if theme == "dark" else None

        output_path = os.path.join(WORKDIR, f"carousel_{today}_{page_num}.jpg")
        build_slide(
            photo_path=photo_path,
            output_path=output_path,
            category_label=topic["category"],
            page_num=page_num,
            page_total=page_total,
            headline_lines=slide["headline_lines"],
            body_text=slide["body_text"],
            panels=slide["panels"],
            takeaway_text=slide["takeaway_text"],
            cta_text=slide["cta_text"],
            top_left_tagline=slide.get("top_left_tagline"),
            top_right_words=slide.get("top_right_words"),
            corner_left_words=corner_left,
            corner_right_words=corner_right,
            theme=theme,
            rtl=rtl,
        )
        image_urls.append(_host(today, output_path))
        os.remove(output_path)

    first, mid, last = topic["slides"][0], topic["slides"][len(topic["slides"]) // 2], topic["slides"][-1]
    hook = " ".join(t for t, _ in first["headline_lines"])
    caption = build_caption(hook=hook, tip=mid["body_text"], cta=last["cta_text"],
                             disclaimer=disclaimer, state=st)
    return {"type": "carousel", "image_urls": image_urls, "caption": caption}


def run_generate() -> None:
    os.makedirs(WORKDIR, exist_ok=True)
    today_date = datetime.date.today()
    today = today_date.isoformat()
    weekday = today_date.weekday()
    lang = "en" if weekday in ENGLISH_WEEKDAYS else "fa"
    st = state_mod.load()

    print(f"[{today}] Language for today: {lang}")

    items = [build_reel_item(today, st, lang)]
    state_mod.save(st)

    items.extend(build_story_items(today, st, lang))
    state_mod.save(st)

    if weekday in CAROUSEL_WEEKDAYS:
        items.append(build_carousel_item(today, st, lang))
        state_mod.save(st)
    elif weekday in FEED_POST_WEEKDAYS:
        items.append(build_feed_image_item(today, st, lang))
        state_mod.save(st)
    else:
        print(f"[{today}] No feed/carousel post scheduled today.")

    manifest = {"date": today, "items": items}
    manifest_path = os.path.join(WORKDIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    manifest_url = _host(today, manifest_path)
    os.remove(manifest_path)

    print(f"[{today}] Generated {len(items)} item(s).")
    print("MANIFEST_URL:", manifest_url)


def run_publish() -> None:
    manifest_url = os.environ["MANIFEST_URL"]
    resp = requests.get(manifest_url, timeout=30)
    resp.raise_for_status()
    manifest = resp.json()
    today = manifest["date"]

    st = state_mod.load()

    for item in manifest["items"]:
        kind = item["type"]
        if kind == "reel":
            media_id = publish_reel(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                     config.IG_ACCESS_TOKEN, item["video_url"], item["caption"])
        elif kind == "story":
            media_id = publish_story(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                      config.IG_ACCESS_TOKEN, image_url=item["image_url"])
        elif kind == "feed_image":
            media_id = publish_feed_image(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                           config.IG_ACCESS_TOKEN, item["image_url"], item["caption"])
        elif kind == "carousel":
            media_id = publish_carousel(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                         config.IG_ACCESS_TOKEN, item["image_urls"], item["caption"])
        else:
            raise ValueError(f"Unknown manifest item type: {kind}")
        print(f"[{today}] Published {kind}: {media_id}")
        # Stories can't take comments at all, so there's nothing for
        # reply_comments.py to poll -- only track the other types.
        if kind != "story":
            st["posts"].append({"date": today, "type": kind, "ig_media_id": media_id})

    state_mod.save(st)


if __name__ == "__main__":
    if PIPELINE_MODE == "publish":
        run_publish()
    else:
        run_generate()
