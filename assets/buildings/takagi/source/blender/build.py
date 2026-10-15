"""Current reproducible Takagi cumulative pipeline. Blender 4.2.3 required."""
import runpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'cumulative-v2'
runpy.run_path(str(root/'regenerate.py'),run_name='__main__')
runpy.run_path(str(root/'split_runtime.py'),run_name='__main__')
