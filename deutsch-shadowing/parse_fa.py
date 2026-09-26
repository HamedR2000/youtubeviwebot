import pymupdf, re, json
FIX={'اطالعات':'اطلاعات','آنالین':'آنلاین','اخالق':'اخلاق','اخالقی':'اخلاقی','اختالل':'اختلال','استدالل':'استدلال','اصالح':'اصلاح','اصطالح':'اصطلاح','اطالع':'اطلاع','اعالم':'اعلام','الیه':'لایه','انقالب':'انقلاب','باال':'بالا','باالبر':'بالابر','بالت':'باله','تحصیالت':'تحصیلات','تعطیالت':'تعطیلات','دالیل':'دلایل','صالحیت':'صلاحیت','طالق':'طلاق','عادالنه':'عادلانه','عالمت':'علامت','عضالنی':'عضلانی','عقالنی':'عقلانی','عقالنیت':'عقلانیت','غالت':'غلات','فاضالب':'فاضلاب','فوالد':'فولاد','مالقات':'ملاقات','مالیم':'ملایم','مبتال':'مبتلا','محصوالت':'محصولات','معامالت':'معاملات','معموال':'معمولا','ویال':'ویلا','پاالیش':'پالایش','کاال':'کالا','کاالی':'کالای','کالس':'کلاس','کالسی':'کلاسی','کالن':'کلان','کاله':'کلاه','کامال':'کاملا','یخجال':'یخچال','مجددا':'مجدداً'}
def fix(s):
    return re.sub(r'[؀-ۿ‌]+',lambda m:FIX.get(m.group(0),m.group(0)),s)
isfa=lambda s: bool(re.search(r'[؀-ۿ]',s))
d=pymupdf.open('/home/user/youtubeviwebot/deutsch-pdfs/unisicher3 Farsi.pdf')
rows=[]
for pi,p in enumerate(d):
    lines=[]
    for b in p.get_text('dict')['blocks']:
        for l in b.get('lines',[]):
            t=''.join(s['text'] for s in l['spans']).strip()
            if not t or 'Deutsch_papioun' in t: continue
            lines.append((round(l['bbox'][1]/4),l['bbox'][0],t,max(s['size'] for s in l['spans'])))
    by={}
    for y,x,t,sz in lines: by.setdefault(y,[]).append((x,t,sz))
    for y in sorted(by):
        it=by[y]; fa=any(isfa(t) for _,t,_ in it)
        it.sort(key=lambda a:-a[0] if fa else a[0])
        rows.append((pi+1,' '.join(t for _,t,_ in it).strip(),max(s for *_,s in it)))
entries=[];sec=None;cur=None
for pg,t,sz in rows:
    m=re.match(r'^(\d+\.\d+(?:\.\d+)?)\.?\s*(.*)$',t)
    if sz>=20 or (m and len(t)<40 and not isfa(t)):
        if m: sec=[m.group(1),m.group(2)]
        cur=None; continue
    if sec[1]=='': sec[1]=t; continue
    if isfa(t):
        if cur: cur['fa'].append(fix(t))
    elif cur and not cur['fa'] and not cur['syn']:
        cur['syn'].append(t)
    else:
        cur={'sec':sec[0],'topic':sec[1],'page':pg,'de':t,'fa':[],'syn':[]}; entries.append(cur)
for e in entries:
    e['fa']=' '.join(e['fa']).replace(' ،','،'); e['syn']=' '.join(e['syn'])
json.dump(entries,open('fa_entries.json','w'),ensure_ascii=False,indent=0)
print(len(entries))
import random; random.seed(1)
for e in random.sample(entries,25): print(e['sec'],'|',e['de'],'|',e['fa'],'|',e['syn'])
print('no meaning:',sum(1 for e in entries if not e['fa'] and not e['syn']))
print('syn only:',sum(1 for e in entries if not e['fa'] and e['syn']))
