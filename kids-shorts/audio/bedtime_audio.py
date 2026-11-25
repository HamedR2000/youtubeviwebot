"""Soundtrack for a long bedtime video: a slow music-box lullaby with a soft pad, and a calm narrator at the start.

Usage: python3 audio/bedtime_audio.py <out.wav> <seconds> <lines.json> [seed]
lines.json: [{"t": 3.0, "text": "Good night, cow."}, ...] (said slowly); writes <out.wav>.subs.json with the captions.
Written in 8-second blocks (22.05 kHz mono) so a 30-60 minute track needs little memory.
"""
import json
import os
import sys
import wave

import numpy as np

out, total, lines_file = sys.argv[1], float(sys.argv[2]), sys.argv[3]
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
rng = np.random.default_rng(seed)
SR = 22050
BEAT = 60 / 62  # slow
BAR = 3 * BEAT  # lullaby waltz time
KEY = int(rng.choice([0, 2, 5, -3]))
hz = lambda n: 440.0 * 2 ** ((n - 69) / 12)


def musicbox(n, length=2.6, vol=0.16):
    t = np.arange(int(SR * length), dtype=np.float32) / SR
    f = hz(n)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 3) + 0.12 * np.sin(2 * np.pi * f * 4.02 * t) * np.exp(-t * 6)
    return (vol * s * np.exp(-t * 1.6) * np.minimum(1, t / 0.005)).astype(np.float32)


def pad(notes, length, vol=0.035):
    t = np.arange(int(SR * length), dtype=np.float32) / SR
    s = sum(np.sin(2 * np.pi * hz(n) * t) + 0.25 * np.sin(2 * np.pi * hz(n) * 2.003 * t) for n in notes)
    return (vol * s * np.minimum(1, t / 1.2) * np.minimum(1, (length - t) / 1.2)).astype(np.float32)


CHORDS = [[53, 57, 60], [50, 53, 57], [46, 50, 53], [48, 52, 55]]  # F, Dm, Bb, C
SCALE = [60, 62, 65, 67, 69, 72, 74, 77]  # F major pentatonic-ish
# Twinkle Twinkle Little Star (public domain), in F: (note, beats)
TWINKLE = [(65, 1), (65, 1), (72, 1), (72, 1), (74, 1), (74, 1), (72, 2), (70, 1), (70, 1), (69, 1), (69, 1), (67, 1), (67, 1), (65, 2)]

# narration: TTS once, placed on the global timeline
voice_clips = []
subs = []
lines = json.load(open(lines_file))
if lines and os.environ.get('NARRATION') != '0':
    from kokoro_onnx import Kokoro
    kdir = os.environ.get('KOKORO_DIR', '.')
    tts = Kokoro(os.path.join(kdir, 'kokoro-v1.0.onnx'), os.path.join(kdir, 'voices-v1.0.bin'))
    for ln in lines:
        x, sr = tts.create(ln['text'], voice=ln.get('voice', 'af_heart'), speed=0.82, lang='en-us')
        x = np.asarray(x, dtype=np.float32)
        idx = np.where(np.abs(x) > 0.02 * np.max(np.abs(x)))[0]
        x = x[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.08 * sr)]
        x = np.interp(np.linspace(0, len(x) - 1, int(len(x) * SR / sr)), np.arange(len(x)), x).astype(np.float32)
        x = x / (np.max(np.abs(x)) + 1e-9) * 0.55
        voice_clips.append((int(ln['t'] * SR), x))
        subs.append({'text': ln['text'], 'start': round(ln['t'], 3), 'end': round(ln['t'] + len(x) / SR, 3)})

N = int(total * SR)
BLOCK = int(8 * SR)
TAIL = int(4 * SR)
carry = np.zeros(TAIL, dtype=np.float32)
w = wave.open(out, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)

# pre-compose the whole score as (time, signal-maker) events, then render block by block
events = []
t, bar = 0.0, 0
while t < total:
    ch = [n + KEY for n in CHORDS[bar % 4]]
    events.append((t, ('pad', ch, BAR + 0.6)))
    events.append((t, ('box', ch[0] - 12, 3.0, 0.10)))
    if not ((bar // 8) % 3 == 2 and bar % 8 < 7):  # gentle random melody (every third section is Twinkle instead)
        for b in (0, 1, 2) if rng.random() < 0.5 else (0, 2):
            events.append((t + b * BEAT, ('box', int(rng.choice(SCALE)) + KEY, 2.6, 0.13)))
    t += BAR; bar += 1
# Twinkle phrases placed over the "every third section" bars
t, bar = 0.0, 0
while t < total:
    if (bar // 8) % 3 == 2 and bar % 8 == 0:
        tt = t
        for n, beats in TWINKLE * 1:
            events.append((tt, ('box', n + KEY, 2.4, 0.15))); tt += beats * BEAT * 1.15
    t += BAR; bar += 1
events.sort(key=lambda e: e[0])

ei = 0
for start in range(0, N, BLOCK):
    buf = np.zeros(BLOCK + TAIL, dtype=np.float32)
    buf[:TAIL] += carry
    while ei < len(events) and events[ei][0] * SR < start + BLOCK:
        at, ev = events[ei]; ei += 1
        sig = pad(ev[1], ev[2]) if ev[0] == 'pad' else musicbox(ev[1], ev[2], ev[3])
        i = int(at * SR) - start
        if i < 0:
            continue
        j = min(len(buf), i + len(sig)); buf[i:j] += sig[: j - i]
    music = buf.copy()
    vbuf = np.zeros_like(buf)
    for vi, x in voice_clips:
        i = vi - start
        if i + len(x) < 0 or i >= len(buf):
            continue
        a, b = max(0, i), min(len(buf), i + len(x)); vbuf[a:b] += x[a - i: b - i]
    duck = 1 - 0.45 * np.clip(np.convolve(np.abs(vbuf) > 0.01, np.ones(int(0.3 * SR)) / int(0.3 * SR), mode='same') * 3, 0, 1)
    mix = music * 1.45 * duck + vbuf * 1.3
    # fade in / out of the whole track
    tt = (start + np.arange(len(mix))) / SR
    mix *= np.clip(tt / 4, 0, 1) * np.clip((total - tt) / 20, 0, 1)
    n_out = min(BLOCK, N - start)
    w.writeframes((np.clip(mix[:n_out], -1, 1) * 32767 * 0.9).astype(np.int16).tobytes())
    carry = music[BLOCK:BLOCK + TAIL].copy()  # note tails ring on into the next block
w.close()
json.dump(subs, open(out + '.subs.json', 'w'))
print('wrote', out, f'{total / 60:.1f} min')
