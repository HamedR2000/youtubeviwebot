import csv,glob,re,json,collections
S='/tmp/claude-0/-home-user-youtubeviwebot/2f2d11b1-3602-546c-be6f-a6248bc1d1c0/scratchpad'
pages=[];sec='1.1'
for f in sorted(glob.glob(S+'/ocr/p*.tsv')):
    n=int(f[-7:-4])
    rows=[r for r in csv.DictReader(open(f),delimiter='\t',quoting=csv.QUOTE_NONE) if r['level']=='5' and (r['text'] or '').strip()]
    lines=collections.OrderedDict()
    for r in rows:
        for k in('left','top','width','height','conf'): r[k]=float(r[k])
        lines.setdefault((r['block_num'],r['par_num'],r['line_num']),[]).append(r)
    L=sorted(lines.values(),key=lambda ws:(ws[0]['top']))
    for ws in L[:3]:
        m=re.search(r'(\d)\.(\d{1,2})\.',' '.join(w['text'] for w in ws))
        if m: sec=f'{m.group(1)}.{m.group(2)}'; break
    starts=[round(ws[0]['left']/10)*10 for ws in L if 900<ws[0]['left']<1700]
    if not starts: pages.append((n,sec,[],[]));continue
    split=collections.Counter(starts).most_common(1)[0][0]-40
    left=[];right=[]
    for ws in L:
        ws.sort(key=lambda w:w['left'])
        lw=[];rw=[];inright=False
        for i,w in enumerate(ws):
            if not inright and w['left']>=split:
                gap=w['left']-(ws[i-1]['left']+ws[i-1]['width']) if i else 999
                if gap>=45: inright=True
                else: break
            (rw if inright else lw).append(w)
        else:
            if lw: left.append((lw[0]['top'],' '.join(w['text'] for w in lw)))
            if rw: right.append((rw[0]['top'],' '.join(w['text'] for w in rw)))
            continue
        # line with no column gap -> prose/exercise; ignore
    pages.append((n,sec,left,right))
out=[]
for n,sec,left,right in pages:
    txt=''
    for _,t in right:
        txt = txt[:-1]+t if re.search(r'[a-zäöüß]-$',txt) else (txt+' '+t).strip()
    txt=txt.replace('„','"').replace('“','"').replace('‚',"'").replace('‘',"'")
    sents=re.split(r'(?<=[.!?])\s+(?=["(]?[A-ZÄÖÜ])',txt)
    m=[]
    for x in sents:
        if m and re.search(r'\b(z|d|u|bzw|ca|usw|Nr|Dr|evtl|ggf|v|Chr)\.$',m[-1]): m[-1]+=' '+x
        else: m.append(x)
    sents=m
    out.append({'page':n,'sec':sec,'left':[t for _,t in left],'sents':[s.strip() for s in sents if len(s.split())>=4]})
json.dump(out,open(S+'/book.json','w'),ensure_ascii=False,indent=0)
print(sum(len(p['sents']) for p in out),'sentences')
print(collections.Counter(p['sec'] for p in out))
for p in out[20:22]: print(p['page'],p['sec'],p['left'][:8]); print('\n'.join(p['sents'][:10]))
