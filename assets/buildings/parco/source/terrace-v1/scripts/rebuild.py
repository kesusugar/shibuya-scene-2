#!/usr/bin/env python3
"""Regenerate a copied candidate directory from local inputs using exact Blender 4.2.3."""
from pathlib import Path
import argparse, subprocess, sys, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--blender',required=True);p.add_argument('--render',action='store_true');args=p.parse_args()
blender=str(Path(args.blender).resolve());version=subprocess.check_output([blender,'--version'],text=True)
assert version.splitlines()[0].split()[:2]==['Blender','4.2.3'],version.splitlines()[0]
for name in ['geometry','verification','renders']:(ROOT/name).mkdir(exist_ok=True)
assert not (ROOT/'CANDIDATE_FREEZE.json').exists(),'Preserve the frozen review folder. Copy inputs, scripts, registration and verification/floor_coverage/coverage-proof.json to a new empty directory before rebuilding.'
if not (ROOT/'verification/immutable-inputs-start.json').exists():(ROOT/'verification/immutable-inputs-start.json').write_text('[]\n')
for entry in json.loads((ROOT/'inputs/FILE_HASHES.json').read_text()):
 assert hashlib.sha256((ROOT/'inputs'/entry['file']).read_bytes()).hexdigest()==entry['sha256'],entry['file']
def py(name):subprocess.run([sys.executable,str(ROOT/'scripts'/name)],check=True)
def blend(name,*extra):subprocess.run([blender,'-b','-t','4','--python-exit-code','1','--python',str(ROOT/'scripts'/name),*extra],check=True)
py('prepare_geometry.py');blend('build_candidate.py');py('merge_glb.py')
for name in ['verify_preservation.py','verify_terrace_delta.py','verify_core_coverage_portable.py','verify_retained_quantization.py']:py(name)
for name in ['verify_dense_geometry.py','verify_oblique.py','verify_geometry.py','verify_saved_scene.py']:blend(name)
py('measure_geometry.py')
expected='7338ad9fcebf455a82383f938c36d58d817b9a8b0e9b75ff1e3b88ad9e0d9179';actual=hashlib.sha256((ROOT/'parco_terrace_candidate.glb').read_bytes()).hexdigest();assert actual==expected
if args.render:
 blend('render_candidate.py');py('make_comparison_boards.py')
print('REBUILD PASS',actual)
