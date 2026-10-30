#!/usr/bin/env python3
"""Pull a Pinterest board's latest pins via public RSS (read-only, no login). Usage: pull_board.py <board-slug> [outdir]"""
import sys, re, json, os, html, urllib.request
U='michaelrodg0511'
slug=sys.argv[1]; out=sys.argv[2] if len(sys.argv)>2 else f'/Users/rig128gb/Developer/rig-client-mirror-sites/_inputs/pinterest/{slug}'
os.makedirs(out,exist_ok=True)
req=urllib.request.Request(f'https://www.pinterest.com/{U}/{slug}.rss',headers={'User-Agent':'Mozilla/5.0'})
t=urllib.request.urlopen(req,timeout=20).read().decode('utf-8','replace')
items=re.findall(r'<item>(.*?)</item>',t,re.S); idx=[]
for i,it in enumerate(items):
    link=(re.search(r'<link>(.*?)</link>',it) or [None,''])[1]
    title=html.unescape((re.search(r'<title>(.*?)</title>',it,re.S) or [None,''])[1]).strip()
    desc=html.unescape((re.search(r'<description>(.*?)</description>',it,re.S) or [None,''])[1])
    m=re.search(r'https://i\.pinimg\.com/\w+/([0-9a-f/]+\.(?:jpg|png|webp|gif))',desc)
    if not m: continue
    img='https://i.pinimg.com/736x/'+m.group(1); fn=f'{i:02d}-'+m.group(1).split('/')[-1]
    try:
        data=urllib.request.urlopen(urllib.request.Request(img,headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read()
        open(os.path.join(out,fn),'wb').write(data)
    except Exception as e: fn=None
    text=re.sub('<[^>]+>',' ',desc); text=re.sub(r'\s+',' ',text).strip()
    idx.append({'file':fn,'pin':link,'image':img,'title':title,'text':text[:400]})
json.dump({'board':slug,'user':U,'source':'rss','count':len(idx),'pins':idx},open(os.path.join(out,'index.json'),'w'),indent=1)
print(slug,len(idx),'pins', sum(1 for x in idx if x['file']),'images')
