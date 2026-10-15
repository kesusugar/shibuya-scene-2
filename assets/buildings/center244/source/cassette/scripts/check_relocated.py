"""Regenerate from minimal portable inputs in a clean temporary location."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,json,hashlib,os
from PIL import Image,ImageChops,ImageStat
R=Path(__file__).resolve().parents[1]
blender=sys.argv[1] if len(sys.argv)>1 else 'blender'
with tempfile.TemporaryDirectory(prefix='cassette-portable-') as tmp:
 dst=Path(tmp)/'portable'
 for name in ['inputs','scripts']:shutil.copytree(R/name,dst/name,ignore=shutil.ignore_patterns('__pycache__'))
 (dst/'evidence').mkdir();(dst/'output').mkdir()
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 subprocess.run([sys.executable,str(dst/'scripts/add_cassette.py')],check=True,cwd=tmp,env=env)
 subprocess.run([sys.executable,str(dst/'scripts/verify.py')],check=True,cwd=tmp,env=env,stdout=subprocess.DEVNULL)
 with (dst/'evidence/render.log').open('w') as f:subprocess.run([blender,'-b','-t','4','--python',str(dst/'scripts/render_blend.py')],check=True,cwd=tmp,env=env,stdout=f,stderr=subprocess.STDOUT)
 assert (dst/'output/center244.glb').read_bytes()==(R/'output/center244.glb').read_bytes()
 details=json.loads((dst/'evidence/blender.json').read_text());assert details['version']=='4.2.3 LTS' and details['triangles']==48 and details['image_paths_packed']
 pairs={}
 for p in sorted((R/'evidence').glob('*-*.png')):
  a=Image.open(p).convert('RGB');b=Image.open(dst/'evidence'/p.name).convert('RGB');assert a.size==b.size;diff=ImageChops.difference(a,b);peak=max(v[1] for v in diff.getextrema());mean=sum(ImageStat.Stat(diff).mean)/3;assert peak<=1 and mean<=.001,(p.name,peak,mean);pairs[p.name]={'max_channel_difference':peak,'mean_channel_difference':mean}
 report={'pass':True,'minimal_input_folders':['inputs','scripts'],'external_network_required':False,'glb_byte_identical':True,'render_decoded_pixel_comparison':pairs,'blender':details,'blend_regenerated_and_saved':(dst/'output/center244-cassette.blend').is_file(),'note':'Blend container bytes not compared: save paths/session metadata vary; exact same GLB imported and geometry assertions applied.'}
 (R/'evidence/relocated-regeneration.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
