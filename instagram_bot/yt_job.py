"""YouTube-to-Reel pipeline entry point, run by .github/workflows/yt_to_reel.yml
whenever anything under instagram_bot/yt_jobs/ is pushed. Each job is a
folder, yt_jobs/<video_id>/, moving through two steps (see
yt_jobs/README.md for the files and their schema):

  1. job.json only  -> fetch the video's transcript (yt_source.py) into
     transcript.json. The summarizing itself -- picking out the trading
     points and writing them as slides + voiceover lines -- is done in a
     Claude session reading that transcript, which writes content.json.
  2. content.json new or changed -> render the infographic carousel
     (yt_infographic.py) and the 1-2 minute narrated Reel (yt_reel.py),
     host everything as GitHub Release assets (tag yt-<video_id>), and
     write result.json with the URLs plus a manifest.json in the same
     format main.py's "publish" mode posts from -- so publishing after
     approval is the usual daily_post.yml run with that manifest_url.

Never calls the Instagram API itself, and never touches state.json (the
daily pipeline owns that file).

Run as: python instagram_bot/yt_job.py [job_dir ...] (default: every job).
"""
import datetime
import glob
import hashlib
import json
import os
import shutil
import sys
import traceback

sys.path.insert(0, os.path.dirname(__file__))

from config import config
from content_bank import BRAND_HASHTAGS, DISCLAIMER, DISCLAIMER_FA, HASHTAGS
from github_host import upload_release_asset
from yt_infographic import CAROUSEL_SIZE, REEL_SIZE, make_background, render_slide
from yt_reel import build_reel
from yt_source import fetch_transcript

BRAND_HANDLE = "@Goldhamedsignals"
JOBS_DIR = os.path.join(os.path.dirname(__file__), "yt_jobs")
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
WORKDIR = os.path.join(os.path.dirname(__file__), "_build", "yt")
MAX_CAROUSEL_SLIDES = 10  # Instagram's carousel limit
HASHTAGS_PER_POST = 15


def _read(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _sha(path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def _music_for(video_id: str) -> str:
    """Deterministic pick from music/ per video (not the daily rotation
    cursor, which lives in state.json and belongs to main.py)."""
    tracks = sorted(glob.glob(os.path.join(MUSIC_DIR, "*.mp3")) + glob.glob(os.path.join(MUSIC_DIR, "*.m4a")))
    if not tracks:
        raise FileNotFoundError(f"No music in {MUSIC_DIR}")
    return tracks[int(hashlib.md5(video_id.encode()).hexdigest(), 16) % len(tracks)]


def _caption(content: dict) -> str:
    rtl = content.get("lang", "fa") == "fa"
    tags = content.get("hashtags") or HASHTAGS[:HASHTAGS_PER_POST]
    tags = " ".join(BRAND_HASHTAGS + [t for t in tags if t not in BRAND_HASHTAGS])
    return f"{content['caption'].strip()}\n\n{DISCLAIMER_FA if rtl else DISCLAIMER}\n\n{tags}"


def validate(content: dict) -> None:
    slides = content.get("slides") or []
    if not slides:
        raise ValueError("content.json has no slides")
    if len(slides) > MAX_CAROUSEL_SLIDES:
        raise ValueError(f"{len(slides)} slides -- Instagram carousels take at most {MAX_CAROUSEL_SLIDES}")
    for i, s in enumerate(slides, 1):
        if s.get("type") not in ("cover", "point", "summary", "cta"):
            raise ValueError(f"slide {i}: unknown type {s.get('type')!r}")
    if not content.get("caption"):
        raise ValueError("content.json needs a caption")


def fetch_step(job_dir: str, job: dict) -> None:
    print(f"[yt_job] {job_dir}: fetching transcript for {job['url']}")
    data = fetch_transcript(job["url"])
    _write(os.path.join(job_dir, "transcript.json"), data)
    print(f"[yt_job] {job_dir}: '{data['title']}' by {data['author']} -- {len(data['chunks'])} chunks "
          f"({data['language']})")


def render_step(job_dir: str, video_id: str, content_path: str) -> None:
    content = _read(content_path)
    validate(content)
    rtl = content.get("lang", "fa") == "fa"
    theme = content.get("theme", "dark")
    category = content.get("category", "")
    slides = content["slides"]
    out = os.path.join(WORKDIR, video_id)
    os.makedirs(out, exist_ok=True)
    tag = f"yt-{video_id}"

    def host(path):
        return upload_release_asset(config.GITHUB_REPOSITORY, config.GITHUB_TOKEN, tag, path,
                                    release_name=f"YouTube summary {video_id}")

    image_urls = []
    for page, slide in enumerate(slides, 1):
        path = os.path.join(out, f"slide_{page:02d}.jpg")
        render_slide(slide, page, len(slides), CAROUSEL_SIZE, theme, rtl, BRAND_HANDLE, category,
                     background=make_background(CAROUSEL_SIZE, theme, seed=page)).save(path, quality=92)
        image_urls.append(host(path))
    print(f"[yt_job] {video_id}: {len(image_urls)} carousel slides hosted")

    cover_path = os.path.join(out, "reel_cover.jpg")
    render_slide(slides[0], 1, len(slides), REEL_SIZE, theme, rtl, BRAND_HANDLE, category).save(cover_path, quality=92)
    reel_path = os.path.join(out, "reel.mp4")
    info = build_reel(content, reel_path, _music_for(video_id), out, brand=BRAND_HANDLE)
    reel_url, cover_url = host(reel_path), host(cover_path)
    print(f"[yt_job] {video_id}: Reel {info['duration']}s, voiceover={info['voiceover']}")

    caption = _caption(content)
    manifest = {
        "date": datetime.date.today().isoformat(),
        "lang": "fa" if rtl else "en",
        "source": "yt_job",
        "items": [
            {"type": "reel", "video_url": reel_url, "cover_url": cover_url, "caption": caption},
            {"type": "carousel", "image_urls": image_urls, "caption": caption},
        ],
    }
    manifest_path = os.path.join(out, "manifest.json")
    _write(manifest_path, manifest)
    manifest_url = host(manifest_path)

    _write(os.path.join(job_dir, "result.json"), {
        "content_sha": _sha(content_path),
        "rendered_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "reel_url": reel_url,
        "reel_duration_s": info["duration"],
        "voiceover": info["voiceover"],
        "cover_url": cover_url,
        "carousel_urls": image_urls,
        "caption": caption,
        "manifest_url": manifest_url,
    })
    shutil.rmtree(out, ignore_errors=True)
    print("MANIFEST_URL:", manifest_url)


def process(job_dir: str) -> bool:
    """Run whichever step this job is due for. Returns False on failure
    (after recording it in error.txt, so it shows up in the repo too)."""
    video_id = os.path.basename(os.path.normpath(job_dir))
    error_path = os.path.join(job_dir, "error.txt")
    content_path = os.path.join(job_dir, "content.json")
    result_path = os.path.join(job_dir, "result.json")
    try:
        job = _read(os.path.join(job_dir, "job.json"))
        if not os.path.exists(os.path.join(job_dir, "transcript.json")):
            fetch_step(job_dir, job)
        elif os.path.exists(content_path) and (
                not os.path.exists(result_path) or _read(result_path).get("content_sha") != _sha(content_path)):
            render_step(job_dir, video_id, content_path)
        else:
            print(f"[yt_job] {video_id}: nothing to do")
            return True
    except Exception as e:
        traceback.print_exc()
        with open(error_path, "w", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}\n"
                    f"{type(e).__name__}: {e}\n")
        return False
    if os.path.exists(error_path):
        os.remove(error_path)
    return True


def main(argv) -> int:
    jobs = argv or sorted(os.path.dirname(p) for p in glob.glob(os.path.join(JOBS_DIR, "*", "job.json")))
    ok = all([process(j) for j in jobs])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
