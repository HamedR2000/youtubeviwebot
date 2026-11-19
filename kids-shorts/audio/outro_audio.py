"""Soundtrack for the end card (scenes/outro.html): pals say bye, narrator asks grown-ups to like & subscribe.

Usage: python3 audio/outro_audio.py <out.wav> [duration]
Model files are read from $KOKORO_DIR (kokoro-v1.0.onnx, voices-v1.0.bin); NARRATION=0 gives music + SFX only.
"""
import os
import sys
import wave

import numpy as np

SR = 44100
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 6.8
N = int(SR * DUR)
T = dict(bye=0.2, buttons=1.6, ask=2.0, tap=3.6)  # keep in sync with window.TIMELINE in scenes/outro.html
music = np.zeros(N)
voice = np.zeros(N)


def add(buf, sig, start):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if i < N:
        buf[i:j] += sig[: j - i]


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def marimba(n, length=0.8, vol=0.2):
    t = np.arange(int(SR * length)) / SR
    s = np.sin(2 * np.pi * hz(n) * t) + 0.25 * np.sin(2 * np.pi * hz(n) * 4 * t) * np.exp(-t * 18)
    return vol * s * np.exp(-t * 6.0) * np.minimum(1, t / 0.004)


# cheerful outro jingle: C - F - G - C arpeggios
beat = 0.3
for k, ch in enumerate([[60, 64, 67], [65, 69, 72], [67, 71, 74], [72, 76, 79]] * 2):
    for b, n in enumerate(ch + [ch[1]]):
        add(music, marimba(n, 0.6, 0.11), k * 4 * beat / 1.6 + b * beat / 1.6)
    add(music, marimba(ch[0] - 24, 1.0, 0.12), k * 4 * beat / 1.6)
# pop for the buttons, click for each tap, ding for the bell
t = np.arange(int(0.25 * SR)) / SR
pop = np.sin(2 * np.pi * (300 + 900 * np.exp(-t * 25)) * t) * np.exp(-t * 18)
add(music, 0.4 * pop, T['buttons'])
click = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 60)
add(music, 0.35 * click, T['tap'] - 0.9)
add(music, 0.35 * click, T['tap'] + 0.25)
for i, n in enumerate([84, 88, 91, 96]):
    add(music, marimba(n, 0.9, 0.16), T['tap'] + 0.3 + i * 0.07)

if os.environ.get('NARRATION') != '0':
    from kokoro_onnx import Kokoro
    kdir = os.environ.get('KOKORO_DIR', '.')
    tts = Kokoro(os.path.join(kdir, 'kokoro-v1.0.onnx'), os.path.join(kdir, 'voices-v1.0.bin'))

    def say(text, v, speed=1.0):
        x, sr = tts.create(text, voice=v, speed=speed, lang='en-us')
        x = np.asarray(x, dtype=np.float64)
        idx = np.where(np.abs(x) > 0.02 * np.max(np.abs(x)))[0]
        x = x[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.05 * sr)]
        return np.interp(np.linspace(0, len(x) - 1, int(len(x) * SR / sr)), np.arange(len(x)), x)

    add(voice, say('Bye bye, friends!', 'af_sky', 1.05), T['bye'])
    add(voice, 0.95 * say('Grown-ups, like and subscribe, for a new Doodle Pals video every day!', 'af_heart', 1.05), T['ask'])
    voice = voice / (np.max(np.abs(voice)) + 1e-9) * 0.9

env = np.convolve(np.abs(voice) > 0.01, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')
mix = music / (np.max(np.abs(music)) + 1e-9) * 0.5 * (1 - 0.55 * np.clip(env * 3, 0, 1)) + voice
fl = int(0.8 * SR)
mix[-fl:] *= np.linspace(1, 0, fl)
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.92
pcm = (np.stack([mix, mix], axis=1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1])
