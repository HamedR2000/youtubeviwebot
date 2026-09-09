"""Fetch a free, vertical (Reels-friendly) stock video from Pexels that
matches the day's niche keyword, skipping anything already used before
(tracked in state.json).
"""
import random

import requests

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
MIN_DURATION_S = 6
MAX_DURATION_S = 40


class NoStockVideoFound(Exception):
    pass


def find_unused_video(api_key: str, search_terms: list, used_ids: set) -> dict:
    """Try each search term (in a random order) until we find a portrait
    video whose Pexels id hasn't been posted before. Returns a dict with
    keys: id, download_url, width, height, duration.
    """
    terms = list(search_terms)
    random.shuffle(terms)

    for term in terms:
        resp = requests.get(
            PEXELS_SEARCH_URL,
            headers={"Authorization": api_key},
            params={"query": term, "orientation": "portrait", "size": "medium", "per_page": 20},
            timeout=30,
        )
        resp.raise_for_status()
        videos = resp.json().get("videos", [])
        random.shuffle(videos)

        for video in videos:
            if video["id"] in used_ids:
                continue
            if not (MIN_DURATION_S <= video.get("duration", 0) <= MAX_DURATION_S):
                continue

            portrait_files = [
                f for f in video["video_files"]
                if f.get("width") and f.get("height") and f["height"] > f["width"]
            ]
            if not portrait_files:
                continue
            best = max(portrait_files, key=lambda f: f["width"])

            return {
                "id": video["id"],
                "download_url": best["link"],
                "width": best["width"],
                "height": best["height"],
                "duration": video["duration"],
                "search_term": term,
            }

    raise NoStockVideoFound(
        "No unused portrait Pexels video found for any search term -- "
        "add more terms to content_bank.STOCK_SEARCH_TERMS or clear old "
        "entries from state.json's used_pexels_ids."
    )


def download_video(url: str, dest_path: str) -> None:
    with requests.get(url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
