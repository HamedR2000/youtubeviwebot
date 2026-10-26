"""Fetch a YouTube video's title/channel and transcript -- the raw material
the YouTube-to-Reel pipeline (yt_job.py) summarizes into infographic
slides. Runs inside GitHub Actions, never needs a YouTube login.

Tries youtube-transcript-api first (fast, captions only), then yt-dlp's
subtitle download as a fallback. YouTube sometimes blocks cloud IPs
(GitHub's runners included) from fetching captions; two optional repo
secrets get around that if it starts happening:

  YT_PROXY_URL -- an http(s) proxy URL both fetchers route through
  YT_COOKIES   -- a cookies.txt export (Netscape format) yt-dlp sends
"""
import json
import os
import re
import tempfile

import requests

PREFERRED_LANGS = ["fa", "en", "en-US", "en-GB"]
CHUNK_SECONDS = 20


class TranscriptUnavailable(RuntimeError):
    pass


def extract_video_id(url: str) -> str:
    """Accepts watch?v=, youtu.be/, /shorts/, /live/, /embed/ links or a bare id."""
    url = url.strip()
    if re.fullmatch(r"[\w-]{11}", url):
        return url
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/live/|/embed/)([\w-]{11})", url)
    if not m:
        raise ValueError(f"Could not find a YouTube video id in: {url}")
    return m.group(1)


def fetch_metadata(video_id: str) -> dict:
    """Title + channel via the public oEmbed endpoint (no API key needed).
    Non-fatal: the transcript is what matters, metadata is just for credit."""
    try:
        resp = requests.get("https://www.youtube.com/oembed",
                            params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
                            proxies=_requests_proxies(), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return {"title": data.get("title", ""), "author": data.get("author_name", "")}
    except (requests.RequestException, ValueError) as e:
        print(f"[yt_source] oEmbed metadata failed ({e}); continuing without it")
        return {"title": "", "author": ""}


def _requests_proxies():
    proxy = os.environ.get("YT_PROXY_URL")
    return {"http": proxy, "https": proxy} if proxy else None


def _via_transcript_api(video_id: str) -> dict:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import GenericProxyConfig

    proxy = os.environ.get("YT_PROXY_URL")
    api = YouTubeTranscriptApi(proxy_config=GenericProxyConfig(http_url=proxy, https_url=proxy) if proxy else None)
    transcripts = list(api.list(video_id))
    if not transcripts:
        raise TranscriptUnavailable("video has no captions")

    # Human-made captions beat auto-generated ones; within each, prefer
    # Persian, then English, then whatever the video's own language is.
    def rank(t):
        lang_rank = PREFERRED_LANGS.index(t.language_code) if t.language_code in PREFERRED_LANGS \
            else len(PREFERRED_LANGS)
        return (t.is_generated, lang_rank)

    best = sorted(transcripts, key=rank)[0]
    fetched = best.fetch()
    segments = [{"start": s.start, "text": s.text} for s in fetched]
    return {"language": best.language_code, "is_generated": best.is_generated, "segments": segments}


def _via_yt_dlp(video_id: str) -> dict:
    import yt_dlp

    with tempfile.TemporaryDirectory() as tmp:
        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": PREFERRED_LANGS + ["en-orig", ".*-orig"],
            "subtitlesformat": "json3",
            "outtmpl": os.path.join(tmp, "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        if os.environ.get("YT_PROXY_URL"):
            opts["proxy"] = os.environ["YT_PROXY_URL"]
        if os.environ.get("YT_COOKIES"):
            cookie_path = os.path.join(tmp, "cookies.txt")
            with open(cookie_path, "w", encoding="utf-8") as f:
                f.write(os.environ["YT_COOKIES"])
            opts["cookiefile"] = cookie_path

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        files = sorted(f for f in os.listdir(tmp) if f.endswith(".json3"))
        if not files:
            raise TranscriptUnavailable("yt-dlp found no subtitles")
        # Filenames look like <id>.<lang>.json3 -- pick by the same preference.
        by_lang = {f.split(".")[-2]: f for f in files}
        lang = next((l for l in PREFERRED_LANGS if l in by_lang), next(iter(by_lang)))
        with open(os.path.join(tmp, by_lang[lang]), encoding="utf-8") as f:
            data = json.load(f)

    segments = []
    for ev in data.get("events", []):
        text = "".join(seg.get("utf8", "") for seg in ev.get("segs", []) or []).strip()
        if text:
            segments.append({"start": ev.get("tStartMs", 0) / 1000, "text": text})
    if not segments:
        raise TranscriptUnavailable("yt-dlp subtitles were empty")
    return {"language": lang, "is_generated": None, "segments": segments}


def _chunk(segments: list) -> list:
    """Merge caption lines into ~CHUNK_SECONDS blocks, so the committed
    transcript file stays readable and small."""
    chunks, cur, cur_start = [], [], None
    for s in segments:
        if cur_start is None:
            cur_start = s["start"]
        cur.append(s["text"].replace("\n", " "))
        if s["start"] - cur_start >= CHUNK_SECONDS:
            chunks.append({"start": round(cur_start, 1), "text": " ".join(cur)})
            cur, cur_start = [], None
    if cur:
        chunks.append({"start": round(cur_start, 1), "text": " ".join(cur)})
    return chunks


def fetch_transcript(url: str) -> dict:
    video_id = extract_video_id(url)
    meta = fetch_metadata(video_id)

    errors = []
    for name, fn in (("youtube-transcript-api", _via_transcript_api), ("yt-dlp", _via_yt_dlp)):
        try:
            result = fn(video_id)
            print(f"[yt_source] transcript via {name}: lang={result['language']}, "
                  f"{len(result['segments'])} segments")
            break
        except Exception as e:  # each library raises its own zoo of exception types
            errors.append(f"{name}: {type(e).__name__}: {e}")
            print(f"[yt_source] {name} failed: {e}")
    else:
        raise TranscriptUnavailable(" | ".join(errors))

    return {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": meta["title"],
        "author": meta["author"],
        "language": result["language"],
        "is_generated": result["is_generated"],
        "chunks": _chunk(result["segments"]),
    }
