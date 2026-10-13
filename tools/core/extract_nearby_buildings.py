import json,re,math,pathlib,sys
from shapely.geometry import Polygon
from shapely.ops import unary_union
OLD=json.load(open(sys.argv[1]));P=pathlib.Path(sys.argv[2]);P.mkdir(parents=True,exist_ok=True);wanted=['way/204091879','way/521438304','way/451564412','way/1200029947','way/87250190','way/54500467','way/55895868','way/129061813','way/116710254','way/138670889','way/136587834'];osm={b['id']:b for b in OLD['buildings'] if b['id'] in wanted};targets={i:Polygon([(p[0],-p[1]) for p in b['polygon']['outer']]) for i,b in osm.items()};kx=math.cos(math.radians(35.6595))*111320;ky=110574
text=''.join(pathlib.Path(p).read_text() for p in sys.argv[3:]);records=[]
for m in re.finditer(r'<core:cityObjectMember>(.*?)</core:cityObjectMember>',text,re.S):
 block=m.group(1)
 if '<bldg:Building' not in block:continue
 surfaces=[]
 for kind in ['RoofSurface','WallSurface','GroundSurface','OuterFloorSurface','OuterCeilingSurface','ClosureSurface']:
  for s in re.finditer(r'<bldg:'+kind+r'.*?</bldg:'+kind+'>',block,re.S):
   for pos in re.findall(r'<gml:posList[^>]*>([^<]+)</gml:posList>',s.group()):
    v=list(map(float,pos.split()));ring=[[(v[i+1]-139.7005)*kx,(v[i]-35.6595)*ky,v[i+2]] for i in range(0,len(v)-2,3)];surfaces.append({'kind':kind,'ring':ring})
 if not surfaces:continue
 pts=[p for s in surfaces for p in s['ring']]
 if min(p[0] for p in pts)>400 or max(p[0] for p in pts)<-350 or min(p[1] for p in pts)>350 or max(p[1] for p in pts)<-450:continue
 roofs=[Polygon([p[:2] for p in s['ring']]).buffer(0) for s in surfaces if s['kind'] in ['RoofSurface','GroundSurface']];foot=unary_union([p for p in roofs if not p.is_empty]);id=re.search(r'gml:id="([^"]+)"',block).group(1);records.append({'gml_id':id,'surfaces':surfaces,'foot':foot})
matched={}
for id,target in targets.items():
 best=max(records,key=lambda b:b['foot'].intersection(target).area);ratio=best['foot'].intersection(target).area/target.area;pts=[p for s in best['surfaces'] for p in s['ring']];ground=[p[2] for s in best['surfaces'] if s['kind']=='GroundSurface' for p in s['ring']]
 assert ratio>.5,(id,ratio)
 record={'id':id,'name':osm[id]['tags'].get('name',''),'plateau_id':best['gml_id'],'group':'core','kind':'building','ground_tp':min(ground or [p[2] for p in pts]),'top_tp':max(p[2] for p in pts),'matching_overlap_ratio':ratio,'surfaces':[{'kind':s['kind'],'ring':[[round(p[0],3),round(p[1],3),round(p[2]-15,3)] for p in s['ring']]} for s in best['surfaces']]};matched[id]=record;print(id,record['name'],best['gml_id'],ratio,record['ground_tp'],record['top_tp'])
(P/'matched-neighbourhood.json').write_text(json.dumps(matched,ensure_ascii=False,indent=1)+'\n')
