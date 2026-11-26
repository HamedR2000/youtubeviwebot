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
template = topic.get('template', 'draw-shape')
template = {'vehicle': 'animal'}.get(template, template)  # vehicles reuse the animal scene and lines
if template == 'draw-shape':
    shape, thing, art = topic['shape'].lower(), topic['becomes'].lower(), topic['article']
    an = 'an' if shape[0] in 'aeiou' else 'a'
NUMBER_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty']

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


SUBS = []  # captions: what is said and when (written next to the output as <out>.subs.json)
LAST = {'text': ''}


def say(text, speed=0.95, voice=None, shown=None):
    LAST['text'] = text if shown is None else shown
    samples, sr = tts.create(text, voice=voice or a.voice, speed=speed, lang='en-us')
    x = np.asarray(samples, dtype=np.float64)
    # trim leading/trailing silence
    idx = np.where(np.abs(x) > 0.02 * np.max(np.abs(x)))[0]
    if len(idx):
        x = x[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.05 * sr)]
    # resample to 44.1 kHz
    n = int(len(x) * SR / sr)
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


END = float(tl.get('end') or 20.0)  # Short length (some templates run longer than 20 s)
N = int(SR * END)
voice = np.zeros(N)


def place(clip, t, max_len=None):
    if max_len is not None and len(clip) > max_len * SR:  # never run into the next cue
        clip = clip[: int(max_len * SR)] * np.minimum(1, np.linspace(8, 0, int(max_len * SR)))
    if LAST['text']:
        SUBS.append({'text': LAST['text'], 'start': round(t, 3), 'end': round(t + len(clip) / SR, 3)})
        LAST['text'] = ''
    i = int(t * SR)
    j = min(N, i + len(clip))
    voice[i:j] += clip[: j - i]


if template == 'draw-shape':
    gap = tl['letterGap']
    place(say(f"Let's draw {an} {shape}!"), 0.35, 1.9)
    place(say(DRAW_LINE.get(shape, f"Let's draw {an} {shape}!")), 2.6, 3.6)
    place(say("Now, a happy face!"), 7.6, 1.7)
    place(say(f"Look! It's {art} {thing}!"), tl['extras'] + 0.65, 2.4)
    for i, ch in enumerate(topic['shape']):
        place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + len(topic['shape']) * gap + 0.1
    place(say(f"{shape.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say("Can you draw one, too?"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

elif template == 'count':
    n, word, things = topic['n'], topic['word'].lower(), topic['objectName'].lower()
    gap = tl['letterGap']
    place(say(f"Let's count to {word}!"), 0.35, 1.9)
    place(say(f"This is the number {word}!"), 2.6, 2.4)
    nums = tl.get('popNums') or list(range(1, len(tl['pops']) + 1))
    for i, (tp, k) in enumerate(zip(tl['pops'], nums)):
        nxt = tl['pops'][i + 1] if i + 1 < len(tl['pops']) else tl['result']
        place(say(NUMBER_WORDS[k].capitalize() + '!', speed=1.05), tp + 0.05, (nxt - tp) * 0.95)
    place(say(f"{word.capitalize()} {things}!"), tl['result'] + 0.15, tl['word'] - tl['result'] - 0.2)
    for i, ch in enumerate(topic['word']):
        place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + len(topic['word']) * gap + 0.1
    place(say(f"{word.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say(f"Can you count to {word}?"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

elif template == 'abc':
    L, word = topic['letter'], topic['word']
    name, w = LETTER[L], word.lower()
    gap = tl['letterGap']
    place(say(f"Let's learn the letter {name}!", shown=f"Let's learn the letter {L}!"), 0.35, 1.9)
    place(say(f"This is big {name}.", shown=f"This is big {L}."), 2.7, 2.4)
    place(say(f"And little {name}!", shown=f"And little {L.lower()}!"), tl['lower'] - 0.1, tl['object'] - tl['lower'] + 0.05)
    place(say(f"{name.capitalize()} is for {w}!", shown=f"{L} is for {w}!"), tl['isFor'] + 0.1, 2.3)
    place(say(f"{name.capitalize()}, {name}, {w}!", shown=f"{L}, {L}, {w}!"), tl['isFor'] + 2.7, tl['word'] - tl['isFor'] - 2.8)
    for i, ch in enumerate(c for c in word if c.isalpha()):
        place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + tl['letters'] * gap + 0.1
    place(say(f"{w.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say(f"What else starts with {name}?", shown=f"What else starts with {L}?"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

elif template == 'animal':
    # Ellie the Eraser and the animal sounds get their own voices
    ELLIE, ANIMAL = 'af_bella', 'am_puck'
    w, snd, art = topic['word'].lower(), topic['sound'], topic['article']
    snd1 = snd.split()[0].rstrip('!,').lower()
    gap = tl['letterGap']
    place(say(snd, speed=0.85, voice=ANIMAL), tl['sound1'], 1.2)
    place(say(f"Who says {snd1}?"), 1.6, 1.15)
    place(say("Hi, I'm Ellie! Let's erase the scribbles!", speed=1.05, voice=ELLIE), 2.85, 3.3)
    place(say(f"It's {art} {w}!"), tl['itsA'] + 0.05, 1.7)
    place(say(snd, speed=0.85, voice=ANIMAL), tl['bubble'] + 0.05, 1.2)
    place(say(f"The {w} says {snd1}!"), tl['bubble'] + 1.35, tl['word'] - tl['bubble'] - 1.45)
    for i, ch in enumerate(topic['word']):
        if ch.isalpha():
            place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + len(topic['word']) * gap + 0.1
    place(say(f"{w.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say(f"Can you say {snd1}?"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

elif template == 'color':
    COCO = 'bf_lily'
    w, thing = topic['word'].lower(), topic['mainName']
    a1 = 'an' if w[0] in 'aeiou' else 'a'
    gap = tl['letterGap']
    place(say(f"Let's learn the colour {w}!"), 0.35, 1.9)
    place(say("Hi, I'm Coco! Let me colour it!", voice=COCO), 2.25, tl['colour'][0] - 2.2 + 0.6)
    place(say("Colour, colour, colour...", speed=1.05, voice=COCO), tl['colour'][0] + 0.9, 2.0)
    place(say(f"{w.capitalize()} {thing}!" if thing.endswith('s') else f"{a1.capitalize()} {w} {thing}!"), tl['aColour'] + 0.05, 1.9)
    for i, (key, name) in enumerate(topic['extras']):
        line = f"{w.capitalize()}, like a {name}!" if i == 0 else f"And a {w} {name}!"
        place(say(line), tl['extras'][i] + 0.1, 1.8)
    for i, ch in enumerate(topic['word']):
        place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + len(topic['word']) * gap + 0.1
    place(say(f"{w.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say(f"What else is {w}?"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

elif template == 'bodyparts':
    w = topic['word'].lower()
    gap = tl['letterGap']
    place(say("Let's learn about my body!"), 0.35, tl['show'] - 0.5)
    place(say(f"{'These are' if topic['plural'] else 'This is'} my {w}!"), tl['show'] + 0.1, 2.2)
    place(say(topic['action'], speed=1.0), tl['show'] + 2.5, tl['touch'] - tl['show'] - 2.6)
    place(say(f"Touch your {w}! Can you touch your {w}?"), tl['touch'] + 0.1, tl['word'] - tl['touch'] - 0.3)
    for i, ch in enumerate(topic['word']):
        if ch.isalpha():
            place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + len(topic['word']) * gap + 0.1
    place(say(f"{w.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say(f"Where {'are' if topic['plural'] else 'is'} your {w}?"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

elif template == 'feelings':
    w = topic['word'].lower()
    gap = tl['letterGap']
    place(say("How do you feel?"), 0.35, tl['show'] - 0.5)
    place(say(f"I feel {w}!"), tl['show'] + 0.1, tl['why'] - tl['show'] - 0.15)
    place(say(topic['why']), tl['why'] + 0.15, tl['make'] - tl['why'] - 0.3)
    place(say(f"Can you make a {w} face? {topic['action']}"), tl['make'] + 0.1, tl['word'] - tl['make'] - 0.3)
    for i, ch in enumerate(topic['word']):
        if ch.isalpha():
            place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + len(topic['word']) * gap + 0.1
    place(say(f"{w.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say("How do you feel today?"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

elif template == 'colormix':
    COCO = 'bf_lily'
    A, B, Cc = (topic[k]['name'].lower() for k in ('a', 'b', 'c'))
    gap = tl['letterGap']
    place(say("Let's mix colors!"), 0.3, 1.25)
    place(say(f"{A.capitalize()}!"), tl['a'] + 0.05, tl['b'] - tl['a'] - 0.1)
    place(say(f"And {B}!"), tl['b'] + 0.05, tl['mixSay'] - tl['b'] - 0.1)
    place(say("Let's mix them! Stir, stir, stir!", voice=COCO), tl['mixSay'] + 0.05, tl['reveal'] - tl['mixSay'] - 0.2)
    place(say(f"{A.capitalize()} and {B} make {Cc}!"), tl['reveal'] + 0.1, tl['obj'] - tl['reveal'] - 0.2)
    place(say(f"{Cc.capitalize()}, like {topic['like']}!"), tl['obj'] + 0.1, tl['word'] - tl['obj'] - 0.2)
    for i, ch in enumerate(topic['c']['name']):
        if ch.isalpha():
            place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + len(topic['c']['name']) * gap + 0.1
    place(say(f"{Cc.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say(f"What colors make {Cc}?"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

elif template == 'shadow':
    w, art = topic['word'].lower(), topic.get('article') or ''
    gap = tl['letterGap']
    place(say("Who is hiding? Can you guess?"), 0.35, 2.6)
    place(say("Look at the shadow... hmm!"), 3.1, tl['count'][0] - 3.2)
    for k, tc in zip(['Three!', 'Two!', 'One!'], tl['count']):
        place(say(k, speed=1.05), tc + 0.05, 0.9)
    place(say(f"It's {art + ' ' if art else ''}{w}!"), tl['itsA'] + 0.05, tl['extra'] - tl['itsA'] - 0.1)
    place(say(topic.get('extra') or "Yay! Did you get it right?"), tl['extra'] + 0.1, tl['word'] - tl['extra'] - 0.3)
    for i, ch in enumerate(topic['word']):
        if ch.isalpha():
            place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + len(topic['word']) * gap + 0.1
    place(say(f"{w.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say("Did you guess it? Great job!"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

elif template == 'drawalong':
    COCO = 'bf_lily'
    w, art = topic['word'].lower(), topic['article']
    gap, steps = tl['letterGap'], tl['steps']
    place(say(f"Let's draw {art} {w}!"), 0.35, 1.9)
    for i, stp in enumerate(topic['steps']):
        nxt = steps[i + 1] if i + 1 < len(steps) else tl['colour'][0]
        place(say(stp['say']), steps[i] + 0.1, nxt - steps[i] - 0.25)
    place(say("Now, let me colour it!", voice=COCO), tl['colour'][0] - 0.3, 2.0)
    place(say(f"Ta-da! It's {art} {w}!"), tl['done'] + 0.1, tl['word'] - tl['done'] - 0.2)
    for i, ch in enumerate(topic['word']):
        place(say(LETTER[ch], speed=1.15, shown=ch), tl['word'] + i * gap + 0.05, gap * 0.95)
    end_word = tl['word'] + len(topic['word']) * gap + 0.1
    place(say(f"{w.capitalize()}!"), end_word, max(0.6, tl['ask'] - end_word - 0.05))
    place(say(f"Now you draw {art} {w}! Get your crayons!"), tl['ask'] + 0.2, END - tl['ask'] - 0.4)

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
json.dump(SUBS, open(a.out + '.subs.json', 'w'), indent=1)
print('wrote', a.out)
