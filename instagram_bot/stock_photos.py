"""Fetch a free, portrait stock photo from Pexels for feed/story card
backgrounds -- the photo equivalent of stock_media.py's video search.
"""
import random

import requests

PEXELS_PHOTO_SEARCH_URL = "https://api.pexels.com/v1/search"


class NoStockPhotoFound(Exception):
    pass


def find_unused_photo(api_key: str, search_terms: list, used_ids: set) -> dict:
    """Returns a dict with keys: id, download_url, width, height, search_term."""
    terms = list(search_terms)
    random.shuffle(terms)

    for term in terms:
        resp = requests.get(
            PEXELS_PHOTO_SEARCH_URL,
            headers={"Authorization": api_key},
            params={"query": term, "orientation": "portrait", "size": "large", "per_page": 20},
            timeout=30,
        )
        resp.raise_for_status()
        photos = resp.json().get("photos", [])
        random.shuffle(photos)

        for photo in photos:
            if photo["id"] in used_ids:
                continue
            return {
                "id": photo["id"],
                "download_url": photo["src"]["portrait"],
                "width": photo["width"],
                "height": photo["height"],
                "search_term": term,
            }

    raise NoStockPhotoFound(
        "No unused portrait Pexels photo found for any search term -- "
        "add more terms to content_bank.STOCK_SEARCH_TERMS or clear old "
        "entries from state.json's used_pexels_photo_ids."
    )


def download_photo(url: str, dest_path: str) -> None:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(resp.content)
