import json,re,io,wave,os,subprocess,sys
from multiprocessing import Pool
S='/tmp/claude-0/-home-user-youtubeviwebot/2f2d11b1-3602-546c-be6f-a6248bc1d1c0/scratchpad'
import imageio_ffmpeg; FF=imageio_ffmpeg.get_ffmpeg_exe()
sess=json.load(open(S+'/sessions.json'))
def sp(d):
    d=re.sub(r'\s*,\s*-\S*','',d); d=re.sub(r'\+\s*(A|D|Gen|Akk|Dat)\b','',d)
    d=re.sub(r',\s*(ließ|hat|ist)\b.*$','',d); d=d.replace('(+Ordinalzahl)','').replace('etw.','etwas').replace('jdm.','jemandem').replace('jdn.','jemanden')
    return re.sub(r'\s+',' ',d).strip()
voice=None
def init():
    global voice
    from piper import PiperVoice
    voice=PiperVoice.load(S+'/tts/de-thorsten-low.onnx')
def synth(text):
    try: return _synth(text)
    except Exception: return 16000,b'\0\0'*8000
def _synth(text):
    if not re.search(r'[A-Za-zÄÖÜäöüß]',text): raise ValueError
    buf=io.BytesIO()
    with wave.open(buf,'wb') as w: voice.synthesize_wav(text,w) if hasattr(voice,'synthesize_wav') else voice.synthesize(text,w)
    buf.seek(0)
    with wave.open(buf) as w: return w.getframerate(),w.readframes(w.getnframes())
def job(i):
    out=f'{S}/audio/s{i+1:03d}.mp3'
    mf=out[:-4]+'.json'
    if os.path.exists(mf): return i,json.load(open(mf))
    s=sess[i]; items=[('st',k,t) for k,t in enumerate(s['st'])]+[('w',k,sp(w['d'])) for k,w in enumerate(s['w'])]+[('x',k,w['x']) for k,w in enumerate(s['w']) if w['x'] and w['x'] not in s['st']]
    pcm=b'';marks=[];rate=None
    for kind,k,t in items:
        r,fr=synth(t); rate=r
        st=len(pcm)/2/r; pcm+=fr; marks.append([kind,k,round(st,2),round(len(pcm)/2/r,2)]); pcm+=b'\0\0'*int(r*0.35)
    subprocess.run([FF,'-y','-loglevel','error','-f','s16le','-ar',str(rate),'-ac','1','-i','-','-b:a','24k','-ar','22050',out],input=pcm,check=True)
    json.dump(marks,open(mf,'w'))
    return i,marks
if __name__=='__main__':
    os.makedirs(S+'/audio',exist_ok=True)
    n=int(sys.argv[1]) if len(sys.argv)>1 else len(sess)
    with Pool(4,initializer=init) as p: res=dict(p.map(job,range(n)))
    json.dump({str(k+1):v for k,v in res.items()},open(S+'/audio/marks.json','w'))
    print('ok',n)
