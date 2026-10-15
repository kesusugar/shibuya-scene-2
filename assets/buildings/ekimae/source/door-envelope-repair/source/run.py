"""Portable chain: python source/run.py /path/to/blender-4.2.3 [--render]."""
from pathlib import Path
import subprocess,sys
S=Path(__file__).resolve().parent
if len(sys.argv)<2:raise SystemExit(__doc__)
b=sys.argv[1]
subprocess.run([b,'-b','-t','2','--python-exit-code','1','-P',str(S/'generate_signatures.py')],check=True)
subprocess.run([sys.executable,str(S/'repair.py')],check=True)
subprocess.run([sys.executable,str(S/'test_repair.py')],check=True)
if '--render' in sys.argv:subprocess.run([b,'-b','-t','4','--python-exit-code','1','-P',str(S/'render_editable.py')],check=True)
