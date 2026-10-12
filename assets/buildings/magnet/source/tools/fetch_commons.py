# Fetch Commons file metadata (wikitext) and a 1280 px thumbnail per file. Data only; no execution of fetched content.
import sys,re,json,time,subprocess,urllib.parse,os
out,listfile=sys.argv[1],sys.argv[2]
UA="MagnetResearch/1.0 (personal research)"
names=[l.strip() for l in open(listfile) if l.strip()]
meta=json.load(open(out+'/meta.json')) if os.path.exists(out+'/meta.json') else {}
for i,n in enumerate(names):
    if n in meta and os.path.exists(out+'/'+meta[n]['img']):continue
    t=urllib.parse.unquote(n)
    raw=subprocess.run(["curl","-sS","-m","40","-A",UA,"https://commons.wikimedia.org/w/index.php?title="+urllib.parse.quote(t)+"&action=raw"],capture_output=True,text=True).stdout
    g=lambda k:(re.search(r'\|\s*'+k+r'\s*=\s*(.+)',raw,re.I) or [None,'?'])[1].strip()[:160]
    lic=sorted(set(l.split('|')[0].lower() for l in re.findall(r'\{\{\s*(?:self\s*\|)?\s*((?:cc-[a-z0-9.\-]+|cc-zero|pd-[a-z0-9\-]+|GFDL[^|}]*))',raw,re.I)))
    img=meta[n]['img'] if n in meta else f"M{len(meta)+1:03d}.jpg"
    code=subprocess.run(["curl","-sSL","-m","90","-A",UA,"https://commons.wikimedia.org/wiki/Special:FilePath/"+urllib.parse.quote(t[5:])+"?width=1280","-o",out+'/'+img,"-w","%{http_code}"],capture_output=True,text=True).stdout
    meta[n]=dict(img=img,file=t,url="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(t.replace(' ','_')),license=lic,author=re.sub(r'\[\[[^|\]]*\|([^\]]*)\]\]',r'\1',g('author')),date=g('date'),desc=g('description')[:160],http=code)
    if code!='200' and os.path.exists(out+'/'+img): os.remove(out+'/'+img)
    print(img,code,lic,t[:70],flush=True)
    json.dump(meta,open(out+'/meta.json','w'),ensure_ascii=False,indent=1)
    time.sleep(4 if code=="200" else 30)
