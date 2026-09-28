"""Two-voice audio (male: thorsten VITS, female: css10 VITS) per session.

One mp3 per session; marks.json lists [voice, kind, k, start, end] segments.
"""
import json, os, re, subprocess, sys
import numpy as np

S = '/tmp/claude-0/-home-user-youtubeviwebot/2f2d11b1-3602-546c-be6f-a6248bc1d1c0/scratchpad'
M = S + '/cmodels/'
OUT = S + '/audio2'
VOICES = [('m', 'tts_models--de--thorsten--vits', 'model_file.pth'),
          ('f', 'tts_models--de--css10--vits', 'model_file.pth.tar')]
RATE = 22050


def sp(d):
    d = re.sub(r'\s*,\s*-\S*', '', d)
    d = re.sub(r'\+\s*(A|D|Gen|Akk|Dat)\b', '', d)
    d = re.sub(r',\s*(ließ|hat|ist)\b.*$', '', d)
    d = d.replace('(+Ordinalzahl)', '').replace('etw.', 'etwas').replace('jdm.', 'jemandem').replace('jdn.', 'jemanden')
    d = re.sub(r'\s*/\s*', ' oder ', d)
    return re.sub(r'\s+', ' ', d).strip()


def main(worker, nworkers):
    import torch
    torch.set_num_threads(2)
    from TTS.utils.synthesizer import Synthesizer
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    syn = {v: Synthesizer(tts_checkpoint=M + d + '/' + f, tts_config_path=M + d + '/config.json') for v, d, f in VOICES}
    sess = json.load(open(S + '/sessions.json'))
    os.makedirs(OUT, exist_ok=True)
    for i in range(worker, len(sess), nworkers):
        mp3 = f'{OUT}/s{i + 1:03d}.mp3'
        mf = mp3[:-4] + '.json'
        if os.path.exists(mf):
            continue
        s = sess[i]
        items = [('st', k, t) for k, t in enumerate(s['st'])]
        items += [('w', k, sp(w['d'])) for k, w in enumerate(s['w'])]
        items += [('x', k, w['x']) for k, w in enumerate(s['w']) if w['x'] and w['x'] not in s['st']]
        chunks, marks, pos = [], [], 0
        gap = np.zeros(int(RATE * 0.35), dtype=np.float32)
        for kind, k, text in items:
            if not re.search(r'[A-Za-zÄÖÜäöüß]', text):
                continue
            for v in ('m', 'f'):
                try:
                    wav = np.asarray(syn[v].tts(text), dtype=np.float32)
                except Exception:
                    continue
                marks.append([v, kind, k, round(pos / RATE, 2), round((pos + len(wav)) / RATE, 2)])
                chunks += [wav, gap]
                pos += len(wav) + len(gap)
        pcm = np.concatenate(chunks)
        pcm = (np.clip(pcm / max(1e-3, np.abs(pcm).max()) * 0.9, -1, 1) * 32767).astype('<i2').tobytes()
        subprocess.run([ff, '-y', '-loglevel', 'error', '-f', 's16le', '-ar', str(RATE), '-ac', '1', '-i', '-',
                        '-b:a', '40k', mp3], input=pcm, check=True)
        json.dump(marks, open(mf, 'w'))
        print('done', i + 1, flush=True)


if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]))
