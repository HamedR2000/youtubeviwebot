"""Synthesize a gentle, royalty-free soundtrack + SFX for the 'draw a circle' short.

Usage: python3 audio/music.py out.wav
Timings mirror the T object in scenes/draw-circle.html.
"""
import sys
import wave
import numpy as np

SR = 44100
DUR = 20.0
N = int(SR * DUR)
out = np.zeros(N)

T = dict(draw=(2.2, 6.4), fill=7.0, face=8.0, rays=9.4, word=12.6, gap=0.5, ask=16.4)


def note_hz(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def add(sig, start):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if i < N:
        out[i:j] += sig[: j - i]


def marimba(n, length=0.9, vol=0.22):
    t = np.arange(int(SR * length)) / SR
    f = note_hz(n)
    env = np.exp(-t * 6.0)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 18)
    attack = np.minimum(1, t / 0.004)
    return vol * s * env * attack


def pad(notes, length, vol=0.05):
    t = np.arange(int(SR * length)) / SR
    s = sum(np.sin(2 * np.pi * note_hz(n) * t) + 0.3 * np.sin(2 * np.pi * note_hz(n) * 2.001 * t) for n in notes)
    env = np.minimum(1, t / 0.4) * np.minimum(1, (length - t) / 0.4)
    return vol * s * env


# --- music: 104 bpm, C major, I-V-vi-IV ---
beat = 60 / 104
chords = [[48, 52, 55], [43, 47, 50], [45, 48, 52], [41, 45, 48]]
melody = [72, 76, 79, 76, 74, 71, 74, 79, 76, 72, 76, 81, 77, 76, 74, 72]
bar = 4 * beat
t0 = 0.0
k = 0
while t0 < DUR:
    ch = chords[k % 4]
    add(pad(ch, bar + 0.3), t0)
    for b in range(4):
        add(marimba(ch[0] - 12 + (7 if b % 2 else 0), 0.6, 0.13), t0 + b * beat)
    for b in range(4):
        m = melody[(k * 4 + b) % len(melody)]
        add(marimba(m, 0.8, 0.12), t0 + b * beat)
        if b % 2 == 1:
            add(marimba(m + 7 - 12, 0.5, 0.06), t0 + b * beat + beat / 2)
    t0 += bar
    k += 1

# --- SFX ---
rng = np.random.default_rng(7)

# pencil scribble while drawing: band-limited noise with stroke-rate modulation
a, b = T['draw']
L = int((b - a) * SR)
t = np.arange(L) / SR
noise = rng.standard_normal(L)
noise = np.convolve(noise, np.ones(6) / 6, mode='same') - np.convolve(noise, np.ones(60) / 60, mode='same')
scr = noise * (0.55 + 0.45 * np.sin(2 * np.pi * 7 * t) ** 2) * np.minimum(1, t / 0.2) * np.minimum(1, (L / SR - t) / 0.3)
add(0.10 * scr, a)

# pop for the fill
t = np.arange(int(0.25 * SR)) / SR
pop = np.sin(2 * np.pi * (300 + 900 * np.exp(-t * 25)) * t) * np.exp(-t * 18)
add(0.35 * pop, T['fill'])

# boing for the face
t = np.arange(int(0.45 * SR)) / SR
boing = np.sin(2 * np.pi * (220 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 5)) * t) * np.exp(-t * 6)
add(0.25 * boing, T['face'])

# sparkle arpeggio for the rays
for i, n in enumerate([84, 88, 91, 96, 100]):
    add(marimba(n, 0.6, 0.12), T['rays'] + i * 0.07)

# ding per letter, rising
for i, n in enumerate([72, 74, 76, 77, 79, 84]):
    add(marimba(n, 0.7, 0.2), T['word'] + i * T['gap'])

# final chime
for i, n in enumerate([72, 76, 79, 84]):
    add(marimba(n, 1.6, 0.14), T['ask'] + i * 0.09)

# fade out & normalize
fade = np.ones(N)
fl = int(1.2 * SR)
fade[-fl:] = np.linspace(1, 0, fl)
out *= fade
out = out / (np.max(np.abs(out)) + 1e-9) * 0.85

st = np.stack([out, out], axis=1)
pcm = (st * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1])
