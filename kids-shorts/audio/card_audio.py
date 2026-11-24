"""Short soundtrack for a title card: a cheerful jingle with one narrator line on top.

Usage: python3 audio/card_audio.py <out.wav> <duration> "<text>" [--voice af_heart]
Writes <out.wav>.subs.json too (caption for the line). Model files are read from $KOKORO_DIR.
"""
import argparse
import json
import os
import wave

import numpy as np

p = argparse.ArgumentParser()
p.add_argument('out'); p.add_argument('duration', type=float); p.add_argument('text')
p.add_argument('--voice', default='af_heart')
a = p.parse_args()

SR = 44100
N = int(SR * a.duration)
music, voice = np.zeros(N), np.zeros(N)


def add(buf, sig, start):
    i = int(start * SR); j = min(N, i + len(sig))
    if i < N:
        buf[i:j] += sig[: j - i]


def marimba(n, length=0.8, vol=0.2):
    t = np.arange(int(SR * length)) / SR
    f = 440.0 * 2 ** ((n - 69) / 12)
    return vol * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)) * np.exp(-t * 6.0) * np.minimum(1, t / 0.004)


beat = 0.19
for k, ch in enumerate([[60, 64, 67], [65, 69, 72], [67, 71, 74], [72, 76, 79]] * 3):
    for b, nn in enumerate(ch + [ch[1]]):
        add(music, marimba(nn, 0.6, 0.1), k * 4 * beat + b * beat)
    add(music, marimba(ch[0] - 24, 1.0, 0.12), k * 4 * beat)

subs = []
if os.environ.get('NARRATION') != '0':
    from kokoro_onnx import Kokoro
    kdir = os.environ.get('KOKORO_DIR', '.')
    tts = Kokoro(os.path.join(kdir, 'kokoro-v1.0.onnx'), os.path.join(kdir, 'voices-v1.0.bin'))
    x, sr = tts.create(a.text, voice=a.voice, speed=1.0, lang='en-us')
    x = np.asarray(x, dtype=np.float64)
    idx = np.where(np.abs(x) > 0.02 * np.max(np.abs(x)))[0]
    x = x[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.05 * sr)]
    x = np.interp(np.linspace(0, len(x) - 1, int(len(x) * SR / sr)), np.arange(len(x)), x)
    add(voice, x, 0.4)
    subs.append({'text': a.text, 'start': 0.4, 'end': round(0.4 + len(x) / SR, 3)})
    voice = voice / (np.max(np.abs(voice)) + 1e-9) * 0.9

env = np.convolve(np.abs(voice) > 0.01, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')
mix = music / (np.max(np.abs(music)) + 1e-9) * 0.5 * (1 - 0.55 * np.clip(env * 3, 0, 1)) + voice
fl = int(0.6 * SR); mix[-fl:] *= np.linspace(1, 0, fl)
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.92
with wave.open(a.out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix, mix], axis=1) * 32767).astype(np.int16).tobytes())
json.dump(subs, open(a.out + '.subs.json', 'w'))
print('wrote', a.out)
