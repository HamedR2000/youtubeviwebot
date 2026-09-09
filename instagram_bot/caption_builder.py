"""Assemble the Instagram caption from the day's picked hook/tip/CTA plus a
rotating hashtag set. Keeping this separate from content_bank.py means the
"how it's assembled" logic stays out of the raw content lists.
"""
from content_bank import BRAND_HASHTAGS, HASHTAGS
from state import next_rotating

HASHTAGS_PER_POST = 20


def build_caption(hook: str, tip: str, cta: str, disclaimer: str, state: dict) -> str:
    rotating = next_rotating(HASHTAGS, state, "hashtag_cursor", count=HASHTAGS_PER_POST)
    tags = " ".join(BRAND_HASHTAGS + rotating)

    return (
        f"{hook}\n\n"
        f"{tip}\n\n"
        f"{cta}\n\n"
        f"{disclaimer}\n\n"
        f"{tags}"
    )
