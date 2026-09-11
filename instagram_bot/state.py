"""Tiny JSON-file state store: which stock clips / hashtags / hooks were
already used, so the daily job doesn't repeat itself. Persisted at
instagram_bot/state.json and committed back to the repo by the GitHub
Actions workflow after each run.
"""
import json
import os

STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")

_DEFAULT_STATE = {
    "used_pexels_ids": [],        # stock video ids already posted, oldest first
    "used_pexels_photo_ids": [],  # stock photo ids already posted, oldest first
    "hashtag_cursor": 0,          # rotating offset into content_bank.HASHTAGS
    "hook_cursor": 0,             # rotating offset into content_bank.HOOKS
    "tip_cursor": 0,              # rotating offset into content_bank.TIPS
    "cta_cursor": 0,              # rotating offset into content_bank.CTAS
    "story_line_cursor": 0,       # rotating offset into content_bank.STORY_LINES
    "story_line_fa_cursor": 0,    # rotating offset into content_bank.STORY_LINES_FA
    "carousel_topic_cursor": 0,   # rotating offset into carousel_content.CAROUSELS
    "carousel_bg_cursor": 0,      # rotating offset into carousel_backgrounds.BACKGROUNDS
    "carousel_theme_cursor": 0,   # rotating offset into main.THEME_ORDER (carousel posts)
    "story_theme_cursor": 0,      # rotating offset into main.THEME_ORDER (stories)
    "feed_theme_cursor": 0,       # rotating offset into main.THEME_ORDER (feed image posts)
    "comment_reply_en_cursor": 0,  # rotating offset into content_bank.COMMENT_REPLIES_EN
    "comment_reply_fa_cursor": 0,  # rotating offset into content_bank.COMMENT_REPLIES_FA
    "replied_comment_ids": [],    # comment ids we've already auto-replied to
    "posts": [],                  # history: [{date, type, pexels_id/ig_media_id, ...}, ...]
}

# Cap how much "used" history we keep so Pexels searches don't eventually
# exhaust every result for a niche search term.
MAX_USED_IDS = 200

# Cap replied-comment history so state.json doesn't grow forever.
MAX_REPLIED_IDS = 3000


def load() -> dict:
    if not os.path.exists(STATE_PATH):
        return dict(_DEFAULT_STATE)
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for key, default in _DEFAULT_STATE.items():
        data.setdefault(key, default)
    return data


def save(state: dict) -> None:
    state["used_pexels_ids"] = state["used_pexels_ids"][-MAX_USED_IDS:]
    state["used_pexels_photo_ids"] = state["used_pexels_photo_ids"][-MAX_USED_IDS:]
    state["replied_comment_ids"] = state["replied_comment_ids"][-MAX_REPLIED_IDS:]
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")


def next_rotating(items: list, state: dict, cursor_key: str, count: int = 1):
    """Return `count` items from `items` starting at state[cursor_key],
    wrapping around, and advance the cursor for next time."""
    n = len(items)
    start = state[cursor_key] % n
    picked = [items[(start + i) % n] for i in range(count)]
    state[cursor_key] = (start + count) % n
    return picked
