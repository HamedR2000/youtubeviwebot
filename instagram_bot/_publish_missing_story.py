"""One-off: publish_story on manifest.json's daily-2026-09-15 story_4
failed once with a transient Graph API "media download" error (the
already-hosted GitHub Release asset was, and still is, a valid, publicly
reachable JPEG -- verified by hand). The other 4 stories, the reel, all
posted fine before the pipeline crashed on this one item. Retries just
this single story via the same instagram_publish.publish_story() the
normal pipeline uses, so nothing else gets re-posted. Deleted once no
longer needed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config import config
from instagram_publish import publish_story

STORY_URL = (
    "https://github.com/HamedR2000/youtubeviwebot/releases/download/"
    "daily-2026-09-15/story_2026-09-15_4.jpg"
)


def run() -> None:
    media_id = publish_story(
        config.GRAPH_API_VERSION, config.IG_USER_ID, config.IG_ACCESS_TOKEN,
        image_url=STORY_URL,
    )
    print("PUBLISHED_STORY_ID:", media_id)


if __name__ == "__main__":
    run()
