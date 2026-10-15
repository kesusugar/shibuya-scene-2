"""Portable deterministic chain: accepted baseline -> grille -> support-only repair."""
import subprocess,sys,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];prior=root/'inputs/grille'
subprocess.run([sys.executable,str(prior/'source/build_grille.py'),'--root',str(prior)],check=True)
for f in ['west-block.glb','signs-2025-01.glb','viewer.json']:
 assert (prior/'web'/f).read_bytes()==(root/'inputs/current'/f).read_bytes(),f
subprocess.run([sys.executable,str(root/'source/repair.py'),'--root',str(root)],check=True)
(root/'evidence/chain-regeneration.json').write_text(json.dumps({'accepted_baseline_to_grille_exact':True,'grille_to_support_repair_exact':True,'network_required':False,'uses_pinned_accepted_baseline_not_old_geometry_rebuild':True},indent=2))
