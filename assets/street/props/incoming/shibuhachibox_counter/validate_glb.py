import json,struct,os,math
p=os.path.join(os.path.dirname(__file__),'shibuhachibox_counter.glb')
b=open(p,'rb').read();magic,ver,total=struct.unpack_from('<4sII',b);assert(magic,ver,total)==(b'glTF',2,len(b))
n,t=struct.unpack_from('<II',b,12);assert t==0x4e4f534a;j=json.loads(b[20:20+n]);assert j['asset']['version']=='2.0'
assert all('uri' not in x for x in j.get('buffers',[]));assert all('bufferView' in x and x['mimeType']=='image/png' for x in j.get('images',[]))
assert not j.get('extensionsRequired');assert len(j['materials'])==2
assert not j.get('cameras');assert all('camera' not in x for x in j['nodes'])
tri=0
for mesh in j['meshes']:
 for p in mesh['primitives']:
  assert p.get('mode',4)==4;assert 'POSITION' in p['attributes'];a=j['accessors'][p['indices']];assert a['count']%3==0;tri+=a['count']//3
assert 0<tri<8000
for v in j['bufferViews']:assert v.get('byteOffset',0)+v['byteLength']<=j['buffers'][0]['byteLength']
r={'glb_version':ver,'bytes':len(b),'triangles':tri,'materials':len(j['materials']),'images':len(j['images']),'meshes':len(j['meshes']),'external_resources':False,'required_extensions':j.get('extensionsRequired',[]),'valid':True}
open(os.path.join(os.path.dirname(__file__),'glb_validation.json'),'w').write(json.dumps(r,indent=2));print(json.dumps(r))
