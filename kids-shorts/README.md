# Doodle Pals — kids' YouTube Shorts factory

Code-driven 2D animation for ages 2–6: **Penny the Pencil** draws a simple shape, it turns into a friendly
character (circle → sun, triangle → pizza…), and the English word is spelled out letter by letter.

## Daily flow (with owner approval)
1. A daily Claude scheduled task runs the **Kids Shorts** workflow with `mode=generate`.
2. The workflow renders 5 Shorts (least-recently-used topics, no repeated shape per day, a different
   soundtrack each) and puts them in a pre-release `shorts-YYYY-MM-DD` for review.
3. The owner watches them and approves (optionally rejecting some).
4. The workflow runs again with `mode=publish`, `date=…`, `skip=…` and uploads the approved videos to YouTube
   as *Made for Kids*, category Education.

## Local use
```bash
npm ci
node daily.js --count 5 --out out                         # renders out/<today>/*.mp4 + batch.json
node render.js scenes/draw-shape.html triangle-pizza out/p.mp4 --preview   # stills of one topic
python3 upload.py out/<date> --dry-run                     # show what would be uploaded
```
Output: 1080×1920, 30 fps, H.264 + AAC, 20 s.

## Adding topics
Add an entry to `topics.js`: the shape outline(s) Penny draws (`strokes`), the colour `fill`, `face` position,
and `back`/`front` decoration elements. Preview it with `render.js --preview`.

## YouTube credentials (one-time)
Follow the steps in `get_token.py`, then add repo secrets `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
Note: until the Google API project passes YouTube's API audit, videos uploaded through the API are locked to private.

## Files
- `scenes/draw-shape.html` — SVG scene: `setup(topicId)`, deterministic `render(t)`.
- `render.js` — steps time with Playwright/Chromium and pipes frames into ffmpeg.
- `audio/music.py` — numpy synth music + SFX synced to the scene timeline; seeded per video.
- `audio/narration.py` — English narrator (Kokoro TTS, Apache-2.0, voice `af_heart`) mixed over the ducked music. Needs `KOKORO_DIR` with the model files; set `NARRATION=0` to skip.
- `daily.js` — batch picker/renderer + YouTube metadata. `state/used.json` tracks topic rotation.
- `upload.py` — YouTube Data API uploader.
