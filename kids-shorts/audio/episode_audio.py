"""Build the soundtrack and the timeline of a long episode.

Usage: python3 audio/episode_audio.py <episode.json> <out_dir>   (needs KOKORO_DIR)
Writes <out_dir>/timeline.json (every beat/line/action with times) and <out_dir>/audio.wav.
Line timing comes from the real length of each spoken line, so the picture always follows the voice.
"""
import json
import os
import sys
import wave

import numpy as np
from kokoro_onnx import Kokoro

SR = 44100
VOICES = {'narrator': 'af_heart', 'penny': 'af_sky', 'ellie': 'af_bella', 'coco': 'bf_lily', 'animal': 'am_puck'}
SPEED = {'narrator': 0.92, 'penny': 0.95, 'ellie': 1.0, 'coco': 0.95, 'animal': 0.85}

ep = json.load(open(sys.argv[1]))
out_dir = sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
kdir = os.environ.get('KOKORO_DIR', '.')
tts = Kokoro(os.path.join(kdir, 'kokoro-v1.0.onnx'), os.path.join(kdir, 'voices-v1.0.bin'))


def say(who, text):
    x, sr = tts.create(text, voice=VOICES[who], speed=SPEED[who], lang='en-us')
    x = np.asarray(x, dtype=np.float64)
    idx = np.where(np.abs(x) > 0.02 * np.max(np.abs(x)))[0]
    if len(idx):
        x = x[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)]
    n = int(len(x) * SR / sr)
    x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)
    return x / (np.max(np.abs(x)) + 1e-9) * 0.9


# ---- timeline ----
t = 0.6
clips, beats, sfx, song = [], [], [], []
for b in ep['beats']:
    start = t
    gap = b.get('gap', 0.35)
    lines = []
    lt = start + 0.35
    for who, text in b['say']:
        if who == 'pause':  # silent wait for the child to answer
            lines.append({'who': 'pause', 'text': '', 'start': round(lt, 3), 'dur': float(text)})
            lt += float(text) + gap
            continue
        c = say(who, text)
        lines.append({'who': who, 'text': text, 'start': round(lt, 3), 'dur': round(len(c) / SR, 3)})
        clips.append((lt, c))
        lt += len(c) / SR + gap
    end = max(lt + 0.4, start + b.get('min', 0))
    acts = []
    for a in b.get('do', []):
        a = dict(a); a['t'] = round(start, 3); a['end'] = round(end, 3)
        if 'count' in a or 'tint' in a:  # one pop / colour per spoken line
            a['times'] = [ln['start'] for ln in lines]
            for tt in a['times'][: (a.get('count') or a.get('tint')).get('n', len(lines))]:
                sfx.append(('pop' if 'count' in a else 'sparkle', tt))
        if 'draw' in a:
            a['dur'] = round(min(3.2, max(2.2, end - start - 1.2)), 3)
            sfx.append(('scribble', start + 0.3, a['dur']))
        if 'show' in a: sfx.append(('pop', start + 0.1))
        if 'knock' in a: sfx.append(('knock', start + 0.1))
        if 'erase' in a: sfx.append(('scribble', start + 0.2, 1.2))
        if 'confetti' in a: sfx.append(('sparkle', start + 0.1))
        if 'song' in a: song.append((start, end))
        acts.append(a)
    beats.append({'start': round(start, 3), 'end': round(end, 3), 'lines': lines, 'do': acts})
    t = end
DUR = t + 1.5
json.dump({'id': ep['id'], 'title': ep['title'], 'duration': round(DUR, 3), 'beats': beats}, open(os.path.join(out_dir, 'timeline.json'), 'w'), indent=1)

# ---- music bed: gentle marimba loop, louder during the song ----
N = int(SR * DUR)
music = np.zeros(N); fx = np.zeros(N); voice = np.zeros(N)


def add(buf, sig, start):
    i = int(start * SR); j = min(N, i + len(sig))
    if 0 <= i < N: buf[i:j] += sig[: j - i]


def note_hz(n): return 440.0 * 2 ** ((n - 69) / 12)


def marimba(n, length=0.8, vol=0.2):
    tt = np.arange(int(SR * length)) / SR
    f = note_hz(n)
    return vol * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * f * 4 * tt) * np.exp(-tt * 18)) * np.exp(-tt * 6) * np.minimum(1, tt / 0.004)


def pad(notes, length, vol=0.05):
    tt = np.arange(int(SR * length)) / SR
    s = sum(np.sin(2 * np.pi * note_hz(n) * tt) + 0.3 * np.sin(2 * np.pi * note_hz(n) * 2.001 * tt) for n in notes)
    return vol * s * np.minimum(1, tt / 0.4) * np.minimum(1, (length - tt) / 0.4)


rng = np.random.default_rng(1)
beat = 60 / 104
chords = [[48, 52, 55], [43, 47, 50], [45, 48, 52], [41, 45, 48]]
scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81]
melody, idx = [], 7
for i in range(32):
    idx = int(np.clip(idx + rng.choice([-2, -1, 1, 2, 0]), 4, 12)); melody.append(scale[idx])
t0, k = 0.0, 0
while t0 < DUR:
    ch = chords[k % 4]
    add(music, pad(ch, 4 * beat + 0.3), t0)
    for b_ in range(4):
        add(music, marimba(ch[0] - 12 + (7 if b_ % 2 else 0), 0.6, 0.12), t0 + b_ * beat)
        add(music, marimba(melody[(k * 4 + b_) % 32], 0.8, 0.1), t0 + b_ * beat)
    t0 += 4 * beat; k += 1
gain = np.full(N, 0.45)
for a, b in song:  # music comes up for the sing-along
    gain[int(a * SR): int(b * SR)] = 1.0

# ---- SFX ----
tt = np.arange(int(0.25 * SR)) / SR
POP = np.sin(2 * np.pi * (300 + 900 * np.exp(-tt * 25)) * tt) * np.exp(-tt * 18) * 0.35
KNOCK = sum(np.pad(np.sin(2 * np.pi * 140 * tt[:4000]) * np.exp(-tt[:4000] * 60), (int(i * 0.22 * SR), 0)) for i in range(1)) * 0.6
pc = 0
for e in sfx:
    kind, at = e[0], e[1]
    if kind == 'pop':
        add(fx, POP, at); add(fx, marimba(scale[min(4 + pc % 8, 12)] + 12, 0.5, 0.1), at + 0.03); pc += 1
    elif kind == 'sparkle':
        for i, n in enumerate([84, 88, 91, 96]): add(fx, marimba(n, 0.6, 0.1), at + i * 0.07)
    elif kind == 'knock':
        for i in range(3): add(fx, KNOCK, at + i * 0.25)
    elif kind == 'scribble':
        L = int(e[2] * SR); x = rng.standard_normal(L)
        x = np.convolve(x, np.ones(6) / 6, mode='same') - np.convolve(x, np.ones(60) / 60, mode='same')
        ts = np.arange(L) / SR
        add(fx, 0.08 * x * (0.55 + 0.45 * np.sin(2 * np.pi * 7 * ts) ** 2) * np.minimum(1, ts / 0.2) * np.minimum(1, (L / SR - ts) / 0.3), at)

for at, c in clips:
    add(voice, c, at)
env = np.convolve(np.abs(voice) > 0.01, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')
duck = 1 - 0.55 * np.clip(env * 3, 0, 1)
mix = music / (np.max(np.abs(music)) + 1e-9) * 0.5 * gain * duck + fx + voice
fade = np.ones(N); fl = int(1.5 * SR); fade[-fl:] = np.linspace(1, 0, fl)
mix = mix * fade
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.92
pcm = (np.stack([mix, mix], axis=1) * 32767).astype(np.int16)
with wave.open(os.path.join(out_dir, 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f"{ep['id']}: {DUR:.1f}s, {len(clips)} lines")
