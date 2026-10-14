from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[5]/'tools/core/build_facade.py'),run_name='__main__')
