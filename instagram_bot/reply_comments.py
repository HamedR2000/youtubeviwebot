"""Standalone auto-responder: checks comments on our recent posts and
replies once to each new one with a rotating, language-matched invite to
the free Telegram channel. Uses fixed, pre-approved templates (see
content_bank.COMMENT_REPLIES_EN/FA) -- unlike the daily content pipeline,
this needs no per-run human review, so it runs on its own real cron
(see .github/workflows/reply_comments.yml).

Run as: python reply_comments.py (from inside instagram_bot/).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import state as state_mod
from comment_autoresponder import build_reply
from config import config
from instagram_publish import PublishError, list_comments, reply_to_comment

# How many of our most recent commentable posts to check each run. Older
# posts rarely get new comments, and this bounds API calls as history grows.
RECENT_POSTS_TO_CHECK = 30


def main() -> None:
    st = state_mod.load()
    replied_ids = set(st["replied_comment_ids"])

    recent_media_ids = [
        p["ig_media_id"] for p in st["posts"][-RECENT_POSTS_TO_CHECK:] if p.get("ig_media_id")
    ]

    new_reply_count = 0
    for media_id in recent_media_ids:
        try:
            comments = list_comments(config.GRAPH_API_VERSION, media_id, config.IG_ACCESS_TOKEN)
        except PublishError as e:
            print(f"Skipping media {media_id}: {e}")
            continue

        for comment in comments:
            comment_id = comment["id"]
            if comment_id in replied_ids:
                continue

            message = build_reply(comment.get("username", ""), comment.get("text", ""), st)
            try:
                reply_to_comment(config.GRAPH_API_VERSION, comment_id, config.IG_ACCESS_TOKEN, message)
                print(f"Replied to {comment_id} (@{comment.get('username')}): {message}")
                new_reply_count += 1
            except PublishError as e:
                print(f"Failed to reply to {comment_id}: {e}")
            replied_ids.add(comment_id)

    st["replied_comment_ids"] = list(replied_ids)
    state_mod.save(st)
    print(f"Done. {new_reply_count} new repl{'y' if new_reply_count == 1 else 'ies'}.")


if __name__ == "__main__":
    main()
