from pathlib import Path
import re,json,math
import sys
P=Path(sys.argv[1]);kx=math.cos(math.radians(35.6595))*111320;ky=110574;maps={}
for name in ['TrafficArea','AuxiliaryTrafficArea']:
 s=(P/(name+'_function.xml')).read_text();maps[name]={m.group(2):m.group(1) for m in re.finditer(r'<gml:description>([^<]*)</gml:description>\s*<gml:name[^>]*>([^<]*)</gml:name>',s)}
out=[]
for path in P.glob('*_tran.gml'):
 text=path.read_text()
 for m in re.finditer(r'<tran:(TrafficArea|AuxiliaryTrafficArea)\b.*?</tran:\1>',text,re.S):
  b=m.group();fn=re.search(r'<tran:function[^>]*>([^<]+)</tran:function>',b)
  if not fn:continue
  function=maps[m.group(1)].get(fn.group(1))
  if function not in ['車道部','車道交差部','歩道部','島']:continue
  surface=None;lod=None
  for level in ['lod3','lod2']:
   g=re.search(r'<tran:'+level+r'MultiSurface>.*?</tran:'+level+'MultiSurface>',b,re.S)
   if g:surface=g.group();lod=level;break
  if not surface:continue
  polygons=[]
  def ring_of(part):
   pos=re.search(r'<gml:posList[^>]*>([^<]+)</gml:posList>',part)
   if not pos:return []
   v=list(map(float,pos.group(1).split()));return [[round((v[i+1]-139.7005)*kx,3),round((v[i]-35.6595)*ky,3),v[i+2]] for i in range(0,len(v)-2,3)]
  for poly in re.findall(r'<gml:Polygon\b.*?</gml:Polygon>',surface,re.S):
   exterior=re.search(r'<gml:exterior>.*?</gml:exterior>',poly,re.S)
   if not exterior:continue
   r=ring_of(exterior.group())
   if not r or min(p[0] for p in r)>380 or max(p[0] for p in r)<-330 or min(p[1] for p in r)>350 or max(p[1] for p in r)<-450:continue
   polygons.append({'exterior':r,'interiors':[ring_of(h) for h in re.findall(r'<gml:interior>.*?</gml:interior>',poly,re.S)]})
  if polygons:out.append({'kind':m.group(1),'lod':lod,'function':fn.group(1),'function_ja':function,'polygons':polygons,'tile':path.stem[:8]})
Path(sys.argv[2]).write_text(json.dumps({'traffic_areas':out,'_meta':{'source':'PLATEAU2025 Shibuya transportation; four tiles; original Core preserved'}},ensure_ascii=False,separators=(',',':'))+'\n');from collections import Counter;print(len(out),Counter((t['lod'],t['function_ja']) for t in out))
