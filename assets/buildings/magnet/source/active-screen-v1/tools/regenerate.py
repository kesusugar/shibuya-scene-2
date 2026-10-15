"""Convenience Blender4.2.3 wrapper around unchanged canonical source scripts."""
import bpy,sys,runpy
from pathlib import Path
assert bpy.app.version[:3]==(4,2,3)
r=Path(__file__).resolve().parents[1]
sys.argv=['correct_screen.py','--inputs',str(r/'inputs'),'--output',str(r/'output')]
runpy.run_path(str(r/'source/correct_screen.py'),run_name='__main__')
sys.argv=['build_editable.py','--','--root',str(r)]
runpy.run_path(str(r/'source/build_editable.py'),run_name='__main__')
