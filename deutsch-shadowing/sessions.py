import json,re
S='/tmp/claude-0/-home-user-youtubeviwebot/2f2d11b1-3602-546c-be6f-a6248bc1d1c0/scratchpad'
E_=json.load(open(S+'/entries.json')); B=json.load(open(S+'/book.json'))
TOP='Bildung und Forschung|Mensch|Gesellschaft|Natur und Umwelt|Natur|Wirtschaft|Studium|Sprache|Technik|Medien|Energie|Verkehr|Tourismus|Religion|Geld|Zeit|Freizeit|Sport|Körper|Gesundheit|Ernährung|Biologie|Chemie|Beziehungen|Leben'
def clean(x):
    x=re.sub(r'\s*\d*\s*Wortschatzübungen für Fortgeschrittene\s*\d*\s*',' ',x)
    x=re.sub(r'^(\d\.\s*)?('+TOP+r')\s+(?=[A-ZÄÖÜ])','',x)
    x=re.sub(r'\s*[-—]\s*$','',x); x=re.sub(r'\s+',' ',x).strip()
    return x.replace(' ,',',')
used=set()
for e in E_:
    e['ex']=clean(e['ex']) if e['ex'] else ''
    if e['ex'] and not re.search(r'[.!?"]$',e['ex']) and len(e['ex'])<=40: e['ex']=''
    used.add(e['ex'])
pool={}
for p in B:
    for s in p['sents']:
        c=clean(s)
        if 40<len(c)<220 and c not in used and re.search(r'[.!?]$',c) and not re.search(r'\(\d\)|_|Übung|\.\.\.',c):
            pool.setdefault(p['sec'],[]).append(c)
sess=[]
for i in range(0,len(E_),10):
    ch=E_[i:i+10]; sents=[]
    for e in ch:
        if e['ex'] and e['ex'] not in sents and len(sents)<5: sents.append(e['ex'])
    for sec in [ch[0]['sec'],ch[-1]['sec']]:
        while len(sents)<5 and pool.get(sec): sents.append(pool[sec].pop(0))
    sess.append({'topic':f"{ch[0]['sec']} {ch[0]['topic']}",'w':[{'d':e['de'],'f':e['fa'],'s':e['syn'],'x':e['ex']} for e in ch],'st':sents})
json.dump(sess,open(S+'/sessions.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(sess),'sessions',sum(len(s['st'])<5 for s in sess),'short')
