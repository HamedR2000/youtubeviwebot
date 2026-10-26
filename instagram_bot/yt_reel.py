"""Compose the 1-2 minute vertical Reel for the YouTube-to-Reel pipeline
(yt_job.py) out of yt_infographic.py's slides.

Each slide plays as a sequence of reveal stages (title first, then each
bullet, then the takeaway), every stage held for as long as its line of
voiceover takes, with a short crossfade between stages and a thin gold
progress bar across the top. Voiceover comes from yt_tts.py (ElevenLabs
or OpenAI when their key is set, free edge-tts otherwise). If TTS is
unavailable -- or, the default, content.json doesn't ask for it -- the Reel
is music-only, each stage held for the time its on-screen text takes to
read.

Background music comes from the same music/ bank and rotation as the
daily Reels (video_composer.next_music_track), ducked under the voice.
"""
import bisect
import os

import numpy as np
from moviepy import AudioFileClip, CompositeAudioClip, VideoClip, afx

from video_composer import _scored_clip
from yt_infographic import REEL_SIZE, make_background, render_slide, stage_count
from yt_tts import pick_provider, synthesize

FPS = 30
CROSSFADE_S = 0.4
VOICE_LEAD_S = 0.2      # silence before each line, so it starts after the crossfade
VOICE_TAIL_S = 0.3      # breath after each line before the next stage appears
MUSIC_UNDER_VOICE = 0.3  # extra multiplier on video_composer.MUSIC_VOLUME when narrated


def stage_lines(slide: dict) -> list:
    """What the voiceover says at each reveal stage of a slide. Falls back
    to the on-screen text when a slide doesn't give a separate spoken line."""
    if slide.get("type") != "point":
        return [slide.get("narration") or _flat_title(slide)]
    lines = [slide.get("narration") or slide.get("title", "")]
    for b in slide.get("bullets", []):
        lines.append((b.get("say") or b.get("text")) if isinstance(b, dict) else b)
    if slide.get("takeaway") or slide.get("highlight"):
        hl = slide.get("highlight") or {}
        lines.append(slide.get("takeaway_say") or slide.get("takeaway") or hl.get("label", ""))
    return lines


def stage_texts(slide: dict) -> list:
    """The on-screen text each reveal stage adds -- what a music-only Reel
    times its holds by, so every stage stays up long enough to read."""
    def text_of(x):
        return x.get("text", "") if isinstance(x, dict) else str(x)

    kind = slide.get("type")
    if kind == "cover":
        return [" ".join([_flat_title(slide), slide.get("subtitle", "")]
                         + [text_of(c) for c in slide.get("chips", [])])]
    if kind == "summary":
        return [" ".join([slide.get("title", "")] + list(slide.get("items", [])))]
    if kind == "cta":
        return [" ".join([slide.get("title", ""), slide.get("text", "")]
                         + [text_of(a) for a in slide.get("actions", [])])]
    texts = [slide.get("title", "")] + [text_of(b) for b in slide.get("bullets", [])]
    if slide.get("takeaway") or slide.get("highlight"):
        hl = slide.get("highlight") or {}
        texts.append(" ".join([str(hl.get("value", "")), hl.get("label", ""), slide.get("takeaway", "")]))
    return texts


def _flat_title(slide: dict) -> str:
    title = slide.get("title", "")
    return " ".join(t for t, _ in title) if isinstance(title, list) else title


def _reading_time(text: str) -> float:
    return 1.5 + 0.38 * len(text.split())


def build_reel(content: dict, output_path: str, music_track: str, workdir: str,
               brand: str = "", min_s: float = 60, max_s: float = 120) -> dict:
    """Render the Reel to output_path. Returns {"duration", "voiceover"},
    where voiceover is the TTS provider used, or False for music-only."""
    rtl = content.get("lang", "fa") == "fa"
    theme = content.get("theme", "dark")
    category = content.get("category", "")
    provider = pick_provider(content)
    # Music-only by default: the account owner found even the best free
    # Persian TTS too accented/robotic (2026-10-26). "voiceover": true in
    # content.json turns narration back on.
    use_voice = content.get("voiceover", False)
    slides = content["slides"]

    # 1. Render every reveal stage, and voice (or time) its line.
    frames, lines, shown, voice_paths = [], [], [], []
    for page, slide in enumerate(slides, 1):
        bg = make_background(REEL_SIZE, theme, seed=page)
        spoken, on_screen = stage_lines(slide), stage_texts(slide)
        for k in range(1, stage_count(slide) + 1):
            img = render_slide(slide, page, len(slides), REEL_SIZE, theme, rtl, brand, category,
                               reveal=k, background=bg, numbering=False)
            frames.append(np.asarray(img))
            lines.append(spoken[k - 1] if k - 1 < len(spoken) else "")
            shown.append(on_screen[k - 1] if k - 1 < len(on_screen) else "")

    durations = []
    for i, text in enumerate(lines):
        path = None
        if use_voice and text.strip():
            path = os.path.join(workdir, f"voice_{i:03d}.mp3")
            try:
                synthesize(provider, text, path, content)
            except Exception as e:  # network/service hiccup: fall back to music-only
                print(f"[yt_reel] TTS failed ({type(e).__name__}: {e}); rendering without voiceover")
                use_voice, path = False, None
        voice_paths.append(path)
    if not use_voice:
        voice_paths = [None] * len(lines)

    for text, path in zip(shown, voice_paths):
        if path:
            with AudioFileClip(path) as a:
                durations.append(VOICE_LEAD_S + a.duration + VOICE_TAIL_S)
        else:
            durations.append(_reading_time(text))

    # 2. Fit the 1-2 minute window: stretch holds if short; if long, say so
    #    (cutting would drop content -- trim the script instead).
    total = sum(durations)
    if total < min_s:
        extra = (min_s - total) / len(durations)
        durations = [d + extra for d in durations]
    elif total > max_s and not use_voice:
        durations = [d * max_s / total for d in durations]
    elif total > max_s:
        print(f"[yt_reel] warning: narrated Reel is {total:.0f}s (> {max_s:.0f}s) -- shorten the script")
    starts = np.cumsum([0] + durations[:-1]).tolist()
    total = sum(durations)

    # 3. Video: hold each stage, crossfade into the next, progress bar on top.
    gold = np.array([214, 175, 116], dtype=np.uint8)
    bar_y, bar_h = 22, 8

    def frame_at(t):
        i = max(0, bisect.bisect_right(starts, t) - 1)
        frame = frames[i]
        into = t - starts[i]
        if i > 0 and into < CROSSFADE_S:
            a = into / CROSSFADE_S
            frame = (frames[i - 1] * (1 - a) + frame * a).astype(np.uint8)
        else:
            frame = frame.copy()
        filled = int(REEL_SIZE[0] * min(t / total, 1))
        frame[bar_y:bar_y + bar_h, :, :] = (frame[bar_y:bar_y + bar_h, :, :] * 0.5).astype(np.uint8)
        if rtl:
            frame[bar_y:bar_y + bar_h, REEL_SIZE[0] - filled:, :] = gold
        else:
            frame[bar_y:bar_y + bar_h, :filled, :] = gold
        return frame

    video = VideoClip(frame_function=frame_at, duration=total)

    # 4. Audio: voice lines at their stage starts, music underneath.
    music = _scored_clip(music_track, total, fade_in=1, fade_out=2)
    tracks = [music]
    if use_voice:
        music = music.with_effects([afx.MultiplyVolume(MUSIC_UNDER_VOICE)])
        tracks = [music] + [AudioFileClip(p).with_start(s + VOICE_LEAD_S)
                            for p, s in zip(voice_paths, starts) if p]
    video = video.with_audio(CompositeAudioClip(tracks).with_duration(total))

    video.write_videofile(output_path, fps=FPS, codec="libx264", audio_codec="aac",
                          threads=4, preset="medium", logger=None)
    video.close()
    for p in voice_paths:
        if p and os.path.exists(p):
            os.remove(p)
    return {"duration": round(total, 1), "voiceover": provider if use_voice else False}
