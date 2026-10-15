"""Render-only framing successor. Frozen asset and original renderer are unchanged."""
from pathlib import Path
source=Path(__file__).with_name('render.py').read_text()
source=source.replace("else 52)", "else (36 if name=='rear' else 42 if name in ['front','left','right'] else 52))")
exec(compile(source, str(Path(__file__).with_name('render.py')), 'exec'))
