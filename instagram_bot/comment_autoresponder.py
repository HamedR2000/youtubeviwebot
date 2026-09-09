"""Builds a personalized auto-reply for a comment on one of our own posts:
detects Persian vs English from the comment's own text (simple Unicode
script check -- no external language-detection dependency needed) and
picks a rotating template in that language, addressed to the commenter.
"""
import re

import state as state_mod
from content_bank import COMMENT_REPLIES_EN, COMMENT_REPLIES_FA

_PERSIAN_ARABIC_SCRIPT = re.compile(r"[؀-ۿ]")


def detect_language(comment_text: str) -> str:
    return "fa" if _PERSIAN_ARABIC_SCRIPT.search(comment_text or "") else "en"


def build_reply(username: str, comment_text: str, state: dict) -> str:
    lang = detect_language(comment_text)
    if lang == "fa":
        name = username or "دوست عزیز"
        (template,) = state_mod.next_rotating(COMMENT_REPLIES_FA, state, "comment_reply_fa_cursor")
    else:
        name = username or "there"
        (template,) = state_mod.next_rotating(COMMENT_REPLIES_EN, state, "comment_reply_en_cursor")
    return template.format(name=name)
