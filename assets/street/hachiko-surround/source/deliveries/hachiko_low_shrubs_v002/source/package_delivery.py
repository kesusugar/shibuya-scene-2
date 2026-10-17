from pathlib import Path
import hashlib,json,zipfile,datetime
R=Path(__file__).resolve().parents[1]
files=[]
for folder in ['input','models','textures','evidence']:
 files += [p for p in (R/folder).rglob('*') if p.is_file() and p.suffix not in ['.blend1','.blend2'] and 'preview' not in p.name]
for name in ['build_before.py','build_after.py','create_needle_atlas.py','validate_assets.py','inspect_roundtrip.py','check_glb_winding.py','render_comparisons.py','render_after_final.py','render_close.py','make_comparisons.py','package_delivery.py']:
 files.append(R/'source'/name)
for name in ['asset_validation.json','roundtrip.json','regeneration.json','texture_validation.json','winding_before.json','winding_before.txt','winding_shrubs.json','winding_shrubs.txt','winding_full.json','winding_full.txt','visual_review.json']:
 files.append(R/'validation'/name)
files += [R/'README.md',R/'PROVENANCE.md',R/'MOUNTING.md']
files=sorted(set(files))
for p in files:assert p.is_file(),p
hashes={str(p.relative_to(R)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files}
(R/'SHA256SUMS.txt').write_text(''.join(f"{m['sha256']}  {n}\n" for n,m in hashes.items()))
(R/'MANIFEST.json').write_text(json.dumps({'package':'hachiko_low_shrubs_v002','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blender':'4.2.3 LTS','integration_primary':'models/hachiko_low_shrubs_only_v002.glb','files':hashes},ensure_ascii=False,indent=2)+'\n')
files += [R/'SHA256SUMS.txt',R/'MANIFEST.json']
out=R.parent/'hachiko_low_shrubs_v002_delivery.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,6) as z:
 for p in files:z.write(p,'hachiko_low_shrubs_v002/'+str(p.relative_to(R)))
receipt={'path':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'file_count':len(files)}
(R/'package_receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
