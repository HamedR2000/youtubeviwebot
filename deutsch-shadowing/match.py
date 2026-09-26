import json,re,collections
S='/tmp/claude-0/-home-user-youtubeviwebot/2f2d11b1-3602-546c-be6f-a6248bc1d1c0/scratchpad'
E_=json.load(open(S+'/fa_entries.json')); B=json.load(open(S+'/book.json'))
bysec=collections.defaultdict(list)
for p in B:
    for s in p['sents']:
        s=re.sub(r'^(Bildung und Forschung|Mensch|Gesellschaft|Natur|Leben|Umwelt)\s+','',s)
        if len(s)<25 or len(s)>260 or '(' in s[:3] or re.search(r'\(\d\)|_{2,}|Übung',s): continue
        bysec[p['sec']].append(s)
STOP=set('der die das den dem des ein eine einen einem einer eines sich etwas etw jdn jdm jemand jemanden jemandem jemandes sein haben werden auf aus für mit von zu zum zur an in im bei nach über um vor unter gegen durch ohne und oder nicht als wie es man etwas machen'.split())
def keys(de):
    de=re.sub(r'\+\s*\w+|,\s*-\S*|,\s*(ließ|hat|ist)\b.*|\(.*?\)|[/.;:!?"]',' ',de)
    ws=[w for w in re.findall(r"[A-Za-zÄÖÜäöüß-]+",de) if w.lower() not in STOP and len(w)>2]
    out=[]
    for w in ws:
        s=w.lower()
        if w[0].islower(): s=re.sub(r'(ern|eln|en|n)$','',s) if len(s)>5 else s
        else: s=s[:max(4,len(s)-2)]
        out.append(s)
    return out
secs=list(bysec)
hit=0; used=collections.Counter()
for e in E_:
    ks=keys(e['de']); e['keys']=ks; best=None;bs=0
    cand=bysec.get(e['sec'],[])
    for s in cand:
        sl=s.lower(); sc=sum(len(k) for k in ks if k in sl)
        if sc>0 and ks and (max(ks,key=len) in sl): sc+=5
        sc-=used[s]*3
        if sc>bs: bs=sc;best=s
    if best and bs>=5: e['ex']=best; used[best]+=1; hit+=1
    else: e['ex']=''
print(hit,'/',len(E_))
import random; random.seed(3)
for e in random.sample(E_,20): print(e['de'],'=>',e['ex'])
json.dump(E_,open(S+'/entries.json','w'),ensure_ascii=False,indent=0)
