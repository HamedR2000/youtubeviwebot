"""Soundtrack and timeline of a Doodle Pals song video (16:9, about 3 minutes).

Usage: python3 audio/song_audio.py <song.json> <out_dir>   (needs KOKORO_DIR)
Writes <out_dir>/audio.wav and <out_dir>/timeline.json (sections, every sung word with its time, talk lines).
Structure: intro talk, chorus, then each verse followed by the chorus, then "your turn": the chorus again with
the last word of each line left for the child, and a goodbye.
Vocals: each word spoken in a natural voice exactly on its beat (the owner chose this over a pitch-shifted 'sung' voice);
a soft bell plays the tune.
"""
import json
import os
import re
import sys
import wave

import numpy as np
from kokoro_onnx import Kokoro

song = json.load(open(sys.argv[1]))
out_dir = sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
SR = 44100
BEAT = 60 / song.get('bpm', 100)
KEY = song.get('key', 0)
kdir = os.environ.get('KOKORO_DIR', '.')
tts = Kokoro(os.path.join(kdir, 'kokoro-v1.0.onnx'), os.path.join(kdir, 'voices-v1.0.bin'))
VOICE = {'narrator': 'af_heart', 'penny': 'af_sky', 'ellie': 'af_bella', 'coco': 'bf_lily'}
hz = lambda n: 440.0 * 2 ** ((n - 69) / 12)
_cache = {}


def say(text, voice, speed=1.0):
    k = (text, voice, round(speed, 2))
    if k not in _cache:
        x, sr = tts.create(text, voice=voice, speed=speed, lang='en-us')
        x = np.asarray(x, dtype=np.float64)
        idx = np.where(np.abs(x) > 0.03 * np.max(np.abs(x)))[0]
        x = x[max(0, idx[0] - int(0.01 * sr)): idx[-1] + int(0.03 * sr)] if len(idx) else x
        x = np.interp(np.linspace(0, len(x) - 1, int(len(x) * SR / sr)), np.arange(len(x)), x)
        _cache[k] = x / (np.max(np.abs(x)) + 1e-9)
    return _cache[k]


def chant(word, voice, length):
    x = say(word, voice)
    for sp in (1.15, 1.35, 1.6):
        if len(x) / SR <= length * 0.95:
            break
        x = say(word, voice, sp)
    return x


# ---- arrange ----
t = 0.0
sections, words, talks, clips = [], [], [], []


def talk(who, text, at):
    x = say(text, VOICE[who], 0.95)
    clips.append((at, 0.9 * x)); talks.append({'who': who, 'text': text, 'start': round(at, 3), 'dur': round(len(x) / SR, 3)})
    return len(x) / SR


def block(kind, lines, melody, voices, gaps=False, action=None):
    global t
    start = t
    for li, line in enumerate(lines):
        mel = melody[li % len(melody)]
        bt = t
        for wi, (w, beats) in enumerate(line):
            length = beats * BEAT
            note = mel[min(wi, len(mel) - 1)] + KEY
            gap = gaps and wi == len(line) - 1
            words.append({'text': w, 'start': round(bt, 3), 'dur': round(length, 3), 'line': len([s for s in sections]) * 10 + li,
                          'section': len(sections), 'gap': gap, 'note': note})
            if not gap:
                text = re.sub(r'[^A-Za-z\']', '', w)
                for v in voices:
                    y = chant(text, VOICE[v], length)
                    clips.append((bt + 0.02, 0.8 * y / len(voices) ** 0.5))
            bt += length
        t = bt
    sections.append({'kind': kind, 'start': round(start, 3), 'end': round(t, 3), 'lines': [[w for w, _ in l] for l in lines],
                     'action': action, 'gaps': gaps})


BAR = 4 * BEAT
# intro: 4 bars, the pals say what we do
intro_end = 4 * BAR
talk('penny', song.get('hello', f"Let's sing the {song['title'].lower()}!"), 0.6)
talk('ellie', "Clap along with us!", 0.6 + 3.6)
sections.append({'kind': 'intro', 'start': 0, 'end': round(intro_end, 3)})
t = intro_end
CH = song['chorus']; MEL = song['melody']
order = [('penny', 'ellie'), ('penny',), ('ellie',), ('coco',), ('penny', 'ellie', 'coco')]
block('chorus', CH, MEL['chorus'], order[0])
for k, v in enumerate(song['verses']):
    t += BAR  # one bar: the action is shown and called out
    talk('coco' if k % 2 else 'narrator', v['action'], t - BAR + 0.2)
    block('verse', v['lines'], MEL['verse'], order[1 + k % 3], action=v['action'])
    block('chorus', CH, MEL['chorus'], order[0])
# your turn
talk('penny', "Now you sing! Fill in the words!", t + 0.3)
t += 2 * BAR
block('chorus', CH, MEL['chorus'], ('penny', 'ellie', 'coco'), gaps=True)
talk('coco', song.get('bye', "Great singing! See you next time!"), t + 0.3)
t += 3 * BAR
DUR = t + 1.0

# ---- backing track ----
N = int(DUR * SR)
music = np.zeros(N); voc = np.zeros(N)


def add(buf, sig, at):
    i = int(at * SR); j = min(N, i + len(sig))
    if 0 <= i < N: buf[i:j] += sig[:j - i]


def tone(f, length, vol, decay=4.0, harm=(1, 0.3, 0.1)):
    tt = np.arange(int(length * SR)) / SR
    return vol * sum(h * np.sin(2 * np.pi * f * (k + 1) * tt) for k, h in enumerate(harm)) * np.exp(-tt * decay) * np.minimum(1, tt / 0.005)


tt = np.arange(int(0.25 * SR)) / SR
KICK = np.sin(2 * np.pi * (50 + 120 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12) * 0.6
rng = np.random.default_rng(3)
CLAP = rng.standard_normal(int(0.12 * SR)) * np.exp(-np.arange(int(0.12 * SR)) / SR * 40) * 0.25
HAT = rng.standard_normal(int(0.04 * SR)) * np.exp(-np.arange(int(0.04 * SR)) / SR * 120) * 0.08
CHORDS = {'chorus': [0, 5, 0, 7], 'verse': [0, 7]}
for sec in sections:
    roots = CHORDS.get(sec['kind'], [0, 5, 7, 0])
    b, k = sec['start'], 0
    while b < sec['end'] - 1e-6:
        root = 48 + KEY + roots[(k // 2) % len(roots)]
        for q in range(4):
            at = b + q * BEAT
            add(music, KICK, at) if q in (0, 2) else add(music, CLAP, at)
            add(music, HAT, at + BEAT / 2)
            add(music, tone(hz(root - 12 + (7 if q == 2 else 0)), BEAT * 0.9, 0.22, 3), at)
        for n in (root, root + 4 if (roots[(k // 2) % len(roots)] in (0, 5, 7)) else root + 3, root + 7):
            add(music, tone(hz(n), BAR, 0.05, 0.8, (1, 0.5, 0.2)), b)
        b += BAR; k += 1
for w in words:  # a soft bell doubles the tune (and plays the child's missing words)
    add(music, tone(hz(w['note']), min(w['dur'], 1.2), 0.07 if not w['gap'] else 0.12, 3, (1, 0.2, 0.05)), w['start'])
for at, c in clips:
    add(voc, c, at)
env = np.convolve(np.abs(voc) > 0.02, np.ones(int(0.2 * SR)) / int(0.2 * SR), mode='same')
mix = music / (np.max(np.abs(music)) + 1e-9) * 0.55 * (1 - 0.35 * np.clip(env * 3, 0, 1)) + voc * 0.85
fade = np.ones(N); fade[-int(1.5 * SR):] = np.linspace(1, 0, int(1.5 * SR)); mix *= fade
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.92
with wave.open(os.path.join(out_dir, 'audio.wav'), 'wb') as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
    wv.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
json.dump({'id': song['id'], 'title': song['title'], 'emoji': song.get('emoji', '🎵'), 'banner': song.get('banner', 'Sing along!'), 'bg': song.get('bg', 'bath'), 'duration': round(DUR, 3), 'beat': BEAT,
           'sections': sections, 'words': words, 'talks': talks}, open(os.path.join(out_dir, 'timeline.json'), 'w'), indent=1)
print(f"{song['id']}: {DUR:.1f}s, {len(words)} words")
