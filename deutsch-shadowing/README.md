# Deutsch Shadowing (Uni Sicher)

- `sessions.json`: 179 sessions (10 words + 5 sentences each), in book order.
- Schedule: session 1 = 2026-09-26 20:00 Europe/Berlin, then 09:00 / 14:00 / 20:00 daily.
  Session index = day*3 + slot - 2 (day 0 = 2026-09-26, slot 0/1/2 = 9/14/20).
- `uni-sicher-shadowing.html`: shadowing page (published as a Claude artifact:
  https://claude.ai/artifact/MNrTPNGGPntqj63ptyEys4).
- Scripts: `parse_fa.py` (Farsi PDF → entries), `book.py` (OCR TSV → example sentences),
  `match.py` (entries ↔ sentences), `sessions.py` (bundle into sessions).
- Audio: `gen.py` builds one mp3 per session (Piper, voice de-thorsten-low from rhasspy/piper v0.0.2 release) plus segment timings, embedded in the page as `m`. Audio is published with the artifact under `audio/sNNN.mp3`, not stored in git.
