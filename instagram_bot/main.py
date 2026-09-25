"""Daily entry point, run in one of two modes (env var PIPELINE_MODE):

  generate (default) -- builds today's content (1 Reel, 5 Stories -- each
    a short video with background music, not a plain image -- and either a
    feed image card or a full educational carousel depending on the
    weekday), hosts every asset as a public GitHub Release asset, and
    writes+uploads a manifest.json describing what was built. Does NOT
    call the Instagram API at all -- this is the "show me before it goes
    out" half of the pipeline. Everything posted on a given day is in one
    language -- English on ENGLISH_WEEKDAYS (Mon/Wed/Fri), Persian the
    rest of the week -- see ENGLISH_WEEKDAYS below.

  publish -- takes a manifest URL (env MANIFEST_URL, produced by a prior
    generate run once a human has reviewed and approved it) and actually
    publishes each item to Instagram using the already-hosted assets. No
    regeneration, no new Pexels picks -- what was approved is what posts.
    Right after each Reel/feed post/carousel (not Stories -- they can't
    take comments), also drops the Telegram channel link as the first
    comment (content_bank.FIRST_COMMENT_EN/FA, via
    instagram_publish.create_comment). Also cross-posts the Reel to a
    dedicated YouTube Shorts channel (youtube_publish.upload_short) once
    config.YOUTUBE_CLIENT_ID is set -- see README.md "YouTube Shorts
    setup"; a no-op until then.

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
    FIRST_COMMENT_EN,
    FIRST_COMMENT_FA,
    HOOKS,
    HOOKS_FA,
    STOCK_SEARCH_TERMS,
    STORY_SETS,
    STORY_SETS_FA,
    TIPS,
    TIPS_FA,
)
from github_host import upload_release_asset
from image_composer import build_feed_card, build_story_card
from instagram_publish import (
    PublishError,
    create_comment,
    publish_carousel,
    publish_feed_image,
    publish_reel,
    publish_story,
)
from stock_media import download_video, find_unused_video
from video_composer import compose_story_video, compose_video
from youtube_publish import YouTubePublishError, get_access_token, upload_short

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
    story_sets, cursor_key = (STORY_SETS_FA, "story_set_fa_cursor") if rtl \
        else (STORY_SETS, "story_set_cursor")
    (story_set,) = state_mod.next_rotating(story_sets, st, cursor_key)
    topic, lines = story_set["topic"], story_set["lines"]

    items = []
    for i, line in enumerate(lines):
        (theme,) = state_mod.next_rotating(THEME_ORDER, st, "story_theme_cursor")
        print(f"[{today}] Story {i + 1}/{STORIES_PER_DAY} ('{topic}'): rendering ({theme})...")
        photo_path = next_background(st) if theme == "dark" else None

        card_path = os.path.join(WORKDIR, f"story_{today}_{i}.jpg")
        build_story_card(photo_path, line, BRAND_HANDLE, card_path, rtl=rtl, theme=theme,
                          topic=topic, page_num=i + 1, page_total=len(lines))

        video_path = os.path.join(WORKDIR, f"story_{today}_{i}.mp4")
        compose_story_video(card_path, MUSIC_DIR, video_path)
        video_url = _host(today, video_path)

        os.remove(card_path)
        os.remove(video_path)
        items.append({"type": "story", "video_url": video_url})
    return items


def build_feed_image_item(today: str, st: dict, lang: str) -> dict:
    (theme,) = state_mod.next_rotating(THEME_ORDER, st, "feed_theme_cursor")
    print(f"[{today}] Feed post: theme={theme}")

    photo_path = next_background(st) if theme == "dark" else None

    rtl = lang == "fa"
    hooks, tips, ctas, disclaimer = (HOOKS_FA, TIPS_FA, CTAS_FA, DISCLAIMER_FA) if rtl \
        else (HOOKS, TIPS, CTAS, DISCLAIMER)
    hook_cursor, tip_cursor, cta_cursor = ("hook_fa_cursor", "tip_fa_cursor", "cta_fa_cursor") if rtl \
        else ("hook_cursor", "tip_cursor", "cta_cursor")
    (hook,) = state_mod.next_rotating(hooks, st, hook_cursor)
    (tip,) = state_mod.next_rotating(tips, st, tip_cursor)
    (cta,) = state_mod.next_rotating(ctas, st, cta_cursor)

    output_path = os.path.join(WORKDIR, f"feed_{today}.jpg")
    build_feed_card(photo_path, headline=hook, subtitle=tip, cta=cta,
                     brand_handle=BRAND_HANDLE, output_path=output_path, theme=theme, rtl=rtl)
    caption = build_caption(hook=hook, tip=tip, cta=cta, disclaimer=disclaimer, state=st)
    image_url = _host(today, output_path)

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

    manifest = {"date": today, "lang": lang, "items": items}
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
    lang = manifest.get("lang", "en")
    first_comment = FIRST_COMMENT_FA if lang == "fa" else FIRST_COMMENT_EN

    st = state_mod.load()

    for item in manifest["items"]:
        kind = item["type"]
        if kind == "reel":
            media_id = publish_reel(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                     config.IG_ACCESS_TOKEN, item["video_url"], item["caption"])
        elif kind == "story":
            media_id = publish_story(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                      config.IG_ACCESS_TOKEN, video_url=item["video_url"])
        elif kind == "feed_image":
            media_id = publish_feed_image(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                           config.IG_ACCESS_TOKEN, item["image_url"], item["caption"])
        elif kind == "carousel":
            media_id = publish_carousel(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                         config.IG_ACCESS_TOKEN, item["image_urls"], item["caption"])
        else:
            raise ValueError(f"Unknown manifest item type: {kind}")
        print(f"[{today}] Published {kind}: {media_id}")

        # Cross-post the Reel to the dedicated YouTube Shorts channel too
        # -- optional (config.YOUTUBE_CLIENT_ID is None until
        # youtube_auth_setup.py has been run and the secrets added), and
        # non-fatal like the first-comment step below: a YouTube hiccup
        # should never block the rest of today's Instagram publish run.
        if kind == "reel" and config.YOUTUBE_CLIENT_ID:
            reel_path = os.path.join(WORKDIR, f"reel_{today}_youtube.mp4")
            try:
                download_video(item["video_url"], reel_path)
                access_token = get_access_token(config.YOUTUBE_CLIENT_ID, config.YOUTUBE_CLIENT_SECRET,
                                                 config.YOUTUBE_REFRESH_TOKEN)
                title = item["caption"].splitlines()[0].strip() + " #Shorts"
                video_id = upload_short(access_token, reel_path, title=title, description=item["caption"])
                print(f"[{today}] Uploaded YouTube Short: https://youtube.com/shorts/{video_id}")
            except (YouTubePublishError, requests.RequestException, OSError) as e:
                print(f"[{today}] Could not upload YouTube Short: {e}")
            finally:
                if os.path.exists(reel_path):
                    os.remove(reel_path)

        # Stories can't take comments at all, so there's nothing for
        # reply_comments.py to poll -- only track the other types. Same
        # reason the Telegram-link first comment only goes on these three.
        if kind != "story":
            st["posts"].append({"date": today, "type": kind, "ig_media_id": media_id})
            # Non-fatal: the app's current Graph API permissions may not
            # (yet) include creating fresh top-level comments -- seen in
            # production as "Graph API error 400: (#10) Application does
            # not have permission for this action". That's a Meta App
            # Review / permission-grant issue, not something retrying or
            # code can fix, so don't let it block the rest of today's
            # publish run over a nice-to-have.
            try:
                comment_id = create_comment(config.GRAPH_API_VERSION, media_id, config.IG_ACCESS_TOKEN,
                                             first_comment)
                # Mark our own comment as already-replied so
                # reply_comments.py's scan of this media's comments (which
                # returns everyone's, including ours) never treats it as a
                # commenter to reply to.
                st["replied_comment_ids"].append(comment_id)
                print(f"[{today}] Posted first comment on {kind} {media_id}")
            except PublishError as e:
                print(f"[{today}] Could not post first comment on {kind} {media_id}: {e}")

    state_mod.save(st)


if __name__ == "__main__":
    if PIPELINE_MODE == "publish":
        run_publish()
    else:
        run_generate()
