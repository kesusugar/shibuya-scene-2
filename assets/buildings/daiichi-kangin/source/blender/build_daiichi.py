"""Compatibility entry point. Uses recorded unchanged pavement samples, not a new survey.
Run Blender 4.2.3 -b --python-exit-code 1 -P build_daiichi.py (no arguments).
Legacy four-input CLI is intentionally rejected; see README for the new reproducible command.
"""
import sys, runpy
from pathlib import Path
if '--' in sys.argv and sys.argv[sys.argv.index('--')+1:]:
    raise ValueError('Legacy facade/ground arguments are not supported; run with no arguments. See README.')
runpy.run_path(str(Path(__file__).with_name('build_daiichi_fidelity.py')), run_name='__main__')
