"""Blender 4.2.3 current cumulative revision. Optional -- /path/output.glb."""
from pathlib import Path
import runpy,sys,json
A=Path(__file__).resolve().parents[2]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
output=Path(args[0]).resolve() if args else A/'web/mark-city.glb'
sys.argv=[sys.argv[0],'--',str(output)]
runpy.run_path(str(A/'source/west-cap-v1/source/blender/build.py'),run_name='__main__')
if not args:
 p=A/'source/data/stats.json';stats=json.loads(p.read_text());report=json.loads(output.with_suffix('.east-stats.json').read_text())
 for key in ['triangles','primitives','bytes']:stats[key]=report[key]
 p.write_text(json.dumps(stats,indent=2)+'\n')
