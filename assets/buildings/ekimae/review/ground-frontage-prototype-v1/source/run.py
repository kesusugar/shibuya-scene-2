"""python source/run.py --blender /path/to/blender [--render]. No repository or network needed."""
from pathlib import Path
import argparse,subprocess,sys
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--blender',required=True);p.add_argument('--render',action='store_true');args=p.parse_args()
def blender(script,*flags):subprocess.run([args.blender,'-b','-t','4','--python-exit-code','1','-P',str(R/'source'/script),'--',*flags],check=True)
def python(script):subprocess.run([sys.executable,str(R/'source'/script)],check=True)
blender('provenance.py');python('clip.py');blender('build_addition.py');python('merge.py');python('validate.py');blender('save_editable.py')
if args.render:
 python('fit_cameras.py');blender('render.py');blender('render_photo_cameras.py')
