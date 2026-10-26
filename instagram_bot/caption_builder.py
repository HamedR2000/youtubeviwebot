"""Assemble the Instagram caption from the day's picked hook/tip/CTA plus a
hashtag block. Keeping this separate from content_bank.py means the
"how it's assembled" logic stays out of the raw content lists.
"""
from content_bank import BRAND_HASHTAGS, CORE_HASHTAGS, HASHTAGS, HASHTAGS_FA

# Instagram's documented limit is 30 per caption; 25 keeps a margin (the bot
# has published with up to 21 so far).
MAX_HASHTAGS = 25


def build_hashtags(lang: str = "en", state: dict = None, extra: list = ()) -> str:
    """Brand tags + the language's gold/signal/trading core + any
    post-specific `extra` tags, topped up from the language's rotating pool
    to MAX_HASHTAGS. With `state`, the pool rotates (and advances its
    cursor); without it, the pool is taken from the top."""
    pool, cursor = (HASHTAGS_FA, "hashtag_fa_cursor") if lang == "fa" else (HASHTAGS, "hashtag_cursor")
    tags = []
    for t in BRAND_HASHTAGS + CORE_HASHTAGS.get(lang, CORE_HASHTAGS["en"]) + list(extra):
        if t not in tags:
            tags.append(t)
    room = MAX_HASHTAGS - len(tags)
    start = state[cursor] % len(pool) if state is not None else 0
    candidates = [t for t in pool[start:] + pool[:start] if t not in tags]
    if state is not None:
        state[cursor] = (start + max(room, 0)) % len(pool)
    return " ".join((tags + candidates[:max(room, 0)])[:MAX_HASHTAGS])


def build_caption(hook: str, tip: str, cta: str, disclaimer: str, state: dict, lang: str = "en") -> str:
    tags = build_hashtags(lang, state)
    return (
        f"{hook}\n\n"
        f"{tip}\n\n"
        f"{cta}\n\n"
        f"{disclaimer}\n\n"
        f"{tags}"
    )
