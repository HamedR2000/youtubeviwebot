"""Daily entry point, run in one of two modes (env var PIPELINE_MODE):

  generate (default) -- builds today's content: 5 Stories every day, plus
    -- only on a "content day" (see CONTENT_DAY_ANCHOR below; every other
    calendar day, starting 2026-10-22) -- 1 Reel and either a feed image
    card or a full educational carousel. The account owner asked for this
    on 2026-10-20 after noticing a reel posted every single day felt like
    too much; stories stay daily, everything else now runs every other
    day together instead of its own weekday. Hosts every asset as a public
    GitHub Release asset, and writes+uploads a manifest.json describing
    what was built. Does NOT call the Instagram API at all -- this is the
    "show me before it goes out" half of the pipeline. Everything posted
    on a given day is in one language -- English on ENGLISH_WEEKDAYS (Fri
    only), Persian the rest of the week -- see ENGLISH_WEEKDAYS below.

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
import re
import sys
import time

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
from image_composer import build_feed_card, build_reel_cover, build_story_card
from instagram_publish import (
    PublishError,
    create_comment,
    publish_carousel,
    publish_feed_image,
    publish_reel,
    publish_story,
)
from moviepy import VideoFileClip
from stock_media import NoStockVideoFound, download_video, find_unused_video
from video_composer import (
    compose_slide_videos,
    compose_story_video,
    compose_video,
    extract_cover_frame,
    next_music_track,
)
from youtube_publish import YouTubePublishError, get_access_token, upload_short

BRAND_HANDLE = "@Goldhamedsignals"
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
WORKDIR = os.path.join(os.path.dirname(__file__), "_build")

STORIES_PER_DAY = 5
# Mon=0 ... Sun=6 (datetime.date.weekday())
ENGLISH_WEEKDAYS = {4}          # Fri only: everything posted that day is in English.
                                 # Narrowed from {Mon, Wed, Fri} after the Oct 2026
                                 # engagement review showed Persian reels outperforming
                                 # English ones -- Persian is now the default 6 days/week.

# A known "content day" -- the Reel and the extra feed/carousel post run
# together every other day starting here, alternating forward and backward
# from this date; every day in between is a "content day" too, just an
# even number of days from this anchor. 2026-10-21 (the day before) is the
# first "no reel/post" day. Stories are unaffected -- always daily.
CONTENT_DAY_ANCHOR = datetime.date(2026, 10, 22)

# What the extra post is on a content day, alternating evenly instead of
# being tied to a specific weekday (its own rotation cursor, like the rest
# of the content bank's rotating picks).
POST_TYPE_ROTATION = ["carousel", "feed_image"]


def _is_content_day(d: datetime.date) -> bool:
    return (d - CONTENT_DAY_ANCHOR).days % 2 == 0


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
    # Some Pexels clips (odd multi-track/timecode MP4 muxing, seen
    # 2026-11-09) make moviepy's `ffmpeg -i` probe choke on the download
    # step below. Rather than crash the whole day's generate run over one
    # bad clip, try a handful of different candidates and skip past it.
    skip_ids = set()
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        video_info = find_unused_video(
            api_key=config.PEXELS_API_KEY,
            search_terms=STOCK_SEARCH_TERMS,
            used_ids=set(st["used_pexels_ids"]) | skip_ids,
        )
        raw_path = os.path.join(WORKDIR, f"raw_{video_info['id']}.mp4")
        download_video(video_info["download_url"], raw_path)
        try:
            VideoFileClip(raw_path).close()
            break
        except Exception as exc:
            os.remove(raw_path)
            skip_ids.add(video_info["id"])
            print(f"[{today}] Pexels clip {video_info['id']} unusable ({exc}), trying another "
                  f"(attempt {attempt}/{max_attempts})")
            if attempt == max_attempts:
                raise NoStockVideoFound(
                    f"{max_attempts} Pexels candidates in a row were unusable by moviepy"
                ) from exc

    rtl = lang == "fa"
    hooks, tips, ctas, disclaimer = (HOOKS_FA, TIPS_FA, CTAS_FA, DISCLAIMER_FA) if rtl \
        else (HOOKS, TIPS, CTAS, DISCLAIMER)
    hook_cursor, tip_cursor, cta_cursor = ("hook_fa_cursor", "tip_fa_cursor", "cta_fa_cursor") if rtl \
        else ("hook_cursor", "tip_cursor", "cta_cursor")
    (hook,) = state_mod.next_rotating(hooks, st, hook_cursor)
    (tip,) = state_mod.next_rotating(tips, st, tip_cursor)
    (cta,) = state_mod.next_rotating(ctas, st, cta_cursor)

    output_path = os.path.join(WORKDIR, f"reel_{today}.mp4")
    track_path = next_music_track(MUSIC_DIR, st)
    compose_video(raw_video_path=raw_path, hook=hook, tip=tip, brand_handle=BRAND_HANDLE,
                  track_path=track_path, output_path=output_path, rtl=rtl)

    # A dedicated cover image for the profile grid tile -- without it,
    # Instagram auto-picks a frame from the raw clip with no branding or
    # headline on it at all (the account owner's complaint: reels had no
    # attention-grabbing cover on the profile).
    frame_path = os.path.join(WORKDIR, f"reel_{today}_frame.jpg")
    extract_cover_frame(raw_path, frame_path)
    cover_path = os.path.join(WORKDIR, f"reel_{today}_cover.jpg")
    build_reel_cover(frame_path, hook, BRAND_HANDLE, cover_path, rtl=rtl)
    cover_url = _host(today, cover_path)

    caption = build_caption(hook=hook, tip=tip, cta=cta, disclaimer=disclaimer, state=st, lang=lang)
    video_url = _host(today, output_path)

    st["used_pexels_ids"].append(video_info["id"])
    os.remove(raw_path)
    os.remove(output_path)
    os.remove(frame_path)
    os.remove(cover_path)
    return {"type": "reel", "video_url": video_url, "caption": caption, "cover_url": cover_url}


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
        track_path = next_music_track(MUSIC_DIR, st)
        compose_story_video(card_path, track_path, video_path)
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
    caption = build_caption(hook=hook, tip=tip, cta=cta, disclaimer=disclaimer, state=st, lang=lang)
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

    image_urls, slide_paths = [], []
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
        slide_paths.append(output_path)

    # Music on slide posts too (account owner, 2026-10-26): the same slides
    # as short videos sharing one track; publish falls back to image_urls.
    video_paths = [p[:-4] + ".mp4" for p in slide_paths]
    compose_slide_videos(slide_paths, next_music_track(MUSIC_DIR, st), video_paths)
    video_urls = [_host(today, p) for p in video_paths]
    for p in slide_paths + video_paths:
        os.remove(p)

    first, mid, last = topic["slides"][0], topic["slides"][len(topic["slides"]) // 2], topic["slides"][-1]
    hook = " ".join(t for t, _ in first["headline_lines"])
    caption = build_caption(hook=hook, tip=mid["body_text"], cta=last["cta_text"],
                             disclaimer=disclaimer, state=st, lang=lang)
    return {"type": "carousel", "image_urls": image_urls, "video_urls": video_urls, "caption": caption}


def run_generate() -> None:
    os.makedirs(WORKDIR, exist_ok=True)
    today_date = datetime.date.today()
    today = today_date.isoformat()
    weekday = today_date.weekday()
    lang = "en" if weekday in ENGLISH_WEEKDAYS else "fa"
    content_day = _is_content_day(today_date)
    st = state_mod.load()

    print(f"[{today}] Language for today: {lang}")

    items = []

    if content_day:
        items.append(build_reel_item(today, st, lang))
        state_mod.save(st)
    else:
        print(f"[{today}] No reel today (content-day rotation).")

    items.extend(build_story_items(today, st, lang))
    state_mod.save(st)

    if content_day:
        (post_type,) = state_mod.next_rotating(POST_TYPE_ROTATION, st, "post_type_cursor")
        if post_type == "carousel":
            items.append(build_carousel_item(today, st, lang))
        else:
            items.append(build_feed_image_item(today, st, lang))
        state_mod.save(st)
    else:
        print(f"[{today}] No feed/carousel post today (content-day rotation).")

    manifest = {"date": today, "lang": lang, "items": items}
    manifest_path = os.path.join(WORKDIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    manifest_url = _host(today, manifest_path)
    os.remove(manifest_path)

    print(f"[{today}] Generated {len(items)} item(s).")
    print("MANIFEST_URL:", manifest_url)


def _get_with_retries(url: str, attempts: int = 4, backoff: float = 4.0, timeout: int = 30) -> requests.Response:
    """GitHub's release-asset CDN occasionally 504s for a few minutes at a
    time (seen repeatedly on 2026-11-08) -- retry transient 5xx/connection
    errors with exponential backoff before giving up."""
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code >= 500:
                raise requests.exceptions.HTTPError(f"{resp.status_code} Server Error", response=resp)
            resp.raise_for_status()
            return resp
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            last_exc = exc
            if attempt == attempts:
                break
            wait = backoff * (2 ** (attempt - 1))
            print(f"[retry] fetch failed (attempt {attempt}/{attempts}): {exc} -- retrying in {wait:.0f}s")
            time.sleep(wait)
    raise last_exc


def _fetch_release_asset_via_api(url: str) -> requests.Response:
    """Fallback for _get_with_retries exhausting its attempts against the
    public releases/download CDN (objects.githubusercontent.com) -- fetch
    the same asset through the authenticated REST API instead
    (api.github.com/repos/.../releases/assets/{id}), a different network
    path that isn't always down at the same time (seen 2026-11-08: the
    public CDN flapped 504/200 for ~20 minutes while this path stayed up)."""
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/releases/download/([^/]+)/([^/]+)$", url)
    if not m:
        raise ValueError(f"Can't parse owner/repo/tag/asset from {url}")
    owner, repo, tag, asset_name = m.groups()
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    rel_resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}",
        headers=headers, timeout=30,
    )
    rel_resp.raise_for_status()
    assets = rel_resp.json().get("assets", [])
    asset = next((a for a in assets if a["name"] == asset_name), None)
    if asset is None:
        raise ValueError(f"Asset {asset_name!r} not found in release {tag!r}")

    asset_resp = requests.get(
        asset["url"], headers={**headers, "Accept": "application/octet-stream"}, timeout=30,
    )
    asset_resp.raise_for_status()
    return asset_resp


def _fetch_manifest(url: str) -> requests.Response:
    try:
        return _get_with_retries(url)
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
        print(f"[retry] public CDN exhausted ({exc}) -- falling back to GitHub API")
        return _fetch_release_asset_via_api(url)


def run_publish() -> None:
    manifest_url = os.environ["MANIFEST_URL"]
    resp = _fetch_manifest(manifest_url)
    manifest = resp.json()
    today = manifest["date"]
    lang = manifest.get("lang", "en")
    first_comment = FIRST_COMMENT_FA if lang == "fa" else FIRST_COMMENT_EN

    st = state_mod.load()

    # Lets the account owner approve everything in a generate run except one
    # piece (e.g. "publish the reel, skip the stories today") without a
    # separate generate/review round -- comma-separated manifest item types,
    # passed through from the workflow's skip_types input.
    skip_types = {t.strip() for t in os.environ.get("SKIP_TYPES", "").split(",") if t.strip()}

    # Resume a publish run that already posted some items before failing
    # partway through (e.g. a transient Graph API/CDN error) without
    # reposting them -- comma-separated 0-based indices into manifest.items,
    # passed through from the workflow's skip_item_indices input.
    skip_item_indices = {
        int(i.strip()) for i in os.environ.get("SKIP_ITEM_INDICES", "").split(",") if i.strip()
    }

    for idx, item in enumerate(manifest["items"]):
        kind = item["type"]
        if idx in skip_item_indices:
            print(f"[{today}] Skipping item {idx} ({kind}) (SKIP_ITEM_INDICES)")
            continue
        if kind in skip_types:
            print(f"[{today}] Skipping {kind} (SKIP_TYPES)")
            continue
        if kind == "reel":
            media_id = publish_reel(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                     config.IG_ACCESS_TOKEN, item["video_url"], item["caption"],
                                     cover_url=item.get("cover_url"))
        elif kind == "story":
            media_id = publish_story(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                      config.IG_ACCESS_TOKEN, video_url=item["video_url"])
        elif kind == "feed_image":
            media_id = publish_feed_image(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                           config.IG_ACCESS_TOKEN, item["image_url"], item["caption"])
        elif kind == "carousel":
            media_id = None
            if item.get("video_urls"):
                # Slide videos carry the music; if Instagram rejects them for
                # any reason, still post the slides as plain images rather
                # than lose the post.
                try:
                    media_id = publish_carousel(config.GRAPH_API_VERSION, config.IG_USER_ID,
                                                 config.IG_ACCESS_TOKEN, item["image_urls"], item["caption"],
                                                 video_urls=item["video_urls"])
                except PublishError as e:
                    print(f"[{today}] Video carousel failed ({e}); publishing the image version")
            if media_id is None:
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
