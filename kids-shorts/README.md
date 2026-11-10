# Doodle Pals — kids' YouTube Shorts factory

Code-driven 2D animation for ages 2–6: Penny the Pencil draws a simple shape, it turns into a friendly character, and the English word is spelled out.

## Render
```bash
npm install
python3 audio/music.py out/music.wav                       # synthesized, royalty-free music + SFX
node render.js scenes/draw-circle.html out/draw-circle.mp4 out/music.wav
node render.js scenes/draw-circle.html out/prev.mp4 --preview   # quick stills only
```
Output: 1080×1920, 30 fps, H.264 + AAC, 20 s (YouTube Shorts ready).

## How it works
- `scenes/*.html` — an SVG scene exposing `window.render(t)` (deterministic, frame-exact) and `window.DURATION`.
- `render.js` — steps time with Playwright/Chromium, pipes PNG frames into ffmpeg.
- `audio/music.py` — numpy synth: marimba melody, pad, pencil-scribble, pop, boing, letter dings, synced to the scene timeline.
