"""Add a friendly English narrator (Kokoro TTS, Apache-2.0) to a Short's soundtrack.

Usage: python3 audio/narration.py <music.wav> <timeline.json> <topic.json> <out.wav> [--voice af_heart]
- timeline.json: window.TIMELINE from scenes/draw-shape.html
- topic.json:    {"shape": "CIRCLE", "becomes": "SUN", "article": "a"}
The music is ducked under the voice and the mix is written to out.wav (44.1 kHz stereo).
Model files are read from $KOKORO_DIR (kokoro-v1.0.onnx, voices-v1.0.bin).
"""
import argparse
import json
import os
import wave

import numpy as np
from kokoro_onnx import Kokoro

p = argparse.ArgumentParser()
p.add_argument('music'); p.add_argument('timeline'); p.add_argument('topic'); p.add_argument('out')
p.add_argument('--voice', default='af_heart')
a = p.parse_args()

SR = 44100
tl = json.load(open(a.timeline))
topic = json.load(open(a.topic))
shape, thing, art = topic['shape'].lower(), topic['becomes'].lower(), topic['article']
an = 'an' if shape[0] in 'aeiou' else 'a'

DRAW_LINE = {
    'circle': 'Round and round we go!',
    'square': 'Four straight sides, all the same!',
    'triangle': 'One, two, three sides!',
    'rectangle': 'Two long sides, and two short sides!',
    'oval': 'A long, round shape!',
    'heart': 'Curve down, and curve up!',
    'star': 'Up, and down... five pointy points!',
    'diamond': 'Four slanty sides!',
}
LETTER = dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', [
    'ay', 'bee', 'see', 'dee', 'ee', 'eff', 'jee', 'aitch', 'eye', 'jay', 'kay', 'el', 'em',
    'en', 'oh', 'pee', 'cue', 'are', 'ess', 'tee', 'you', 'vee', 'double you', 'ex', 'why', 'zee']))

kdir = os.environ.get('KOKORO_DIR', '.')
tts = Kokoro(os.path.join(kdir, 'kokoro-v1.0.onnx'), os.path.join(kdir, 'voices-v1.0.bin'))


def say(text, speed=0.95):
    samples, sr = tts.create(text, voice=a.voice, speed=speed, lang='en-us')
    x = np.asarray(samples, dtype=np.float64)
    # trim leading/trailing silence
    idx = np.where(np.abs(x) > 0.02 * np.max(np.abs(x)))[0]
    if len(idx):
        x = x[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.05 * sr)]
    # resample to 44.1 kHz
    n = int(len(x) * SR / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


N = int(SR * 20.0)
voice = np.zeros(N)


def place(clip, t, max_len=None):
    if max_len is not None and len(clip) > max_len * SR:  # never run into the next cue
        clip = clip[: int(max_len * SR)] * np.minimum(1, np.linspace(8, 0, int(max_len * SR)))
    i = int(t * SR)
    j = min(N, i + len(clip))
    voice[i:j] += clip[: j - i]


gap = tl['letterGap']
place(say(f"Let's draw {an} {shape}!"), 0.35, 1.9)
place(say(DRAW_LINE.get(shape, f"Let's draw {an} {shape}!")), 2.6, 3.6)
place(say("Now, a happy face!"), 7.6, 1.7)
place(say(f"Look! It's {art} {thing}!"), tl['extras'] + 0.65, 2.4)
for i, ch in enumerate(topic['shape']):
    place(say(LETTER[ch], speed=1.15), tl['word'] + i * gap + 0.05, gap * 0.95)
end_word = tl['word'] + len(topic['shape']) * gap + 0.1
place(say(f"{shape.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
place(say("Can you draw one, too?"), tl['ask'] + 0.2, 20 - tl['ask'] - 0.4)

voice = voice / (np.max(np.abs(voice)) + 1e-9) * 0.9

# read music (stereo int16) and duck it under the voice
with wave.open(a.music) as w:
    m = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).mean(axis=1) / 32767
m = np.pad(m, (0, max(0, N - len(m))))[:N]
env = np.convolve(np.abs(voice) > 0.01, np.ones(int(0.25 * SR)) / int(0.25 * SR), mode='same')
duck = 1 - 0.6 * np.clip(env * 3, 0, 1)
mix = m * 0.55 * duck + voice
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.92

pcm = (np.stack([mix, mix], axis=1) * 32767).astype(np.int16)
with wave.open(a.out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', a.out)
