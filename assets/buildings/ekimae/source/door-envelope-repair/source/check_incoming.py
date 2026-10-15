"""Read-only incoming overlay gate: python source/check_incoming.py /path/to/repo. Never mutates target."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
repo=Path(sys.argv[1]);pins=json.loads((ROOT/'evidence/accepted_source_pins.json').read_text());errors=[]
for relative,expected in pins.items():
 p=repo/'assets/buildings/ekimae'/relative
 actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
 if actual!=expected:errors.append({'path':str(p),'expected':expected,'actual':actual})
if errors:print(json.dumps({'status':'STOP_INCOMING_CHANGED','differences':errors},indent=2));raise SystemExit(1)
print(json.dumps({'status':'PASS_READ_ONLY_GATE','replacement_path':'assets/buildings/ekimae/web/ekimae.glb','expected_before_sha256':pins['web/ekimae.glb'],'replacement_sha256':hashlib.sha256((ROOT/'web/ekimae.glb').read_bytes()).hexdigest(),'prior_files_not_mutated':True},indent=2))
