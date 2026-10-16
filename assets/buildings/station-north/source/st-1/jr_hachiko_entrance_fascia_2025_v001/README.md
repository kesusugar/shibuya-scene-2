# Relocated JR Miyamasuzaka-side entrance fascia, early-2025 candidate

H-CV-002 · bounded partial candidate · unplaced · not a current-condition or complete-entry reconstruction.

This package independently reconstructs the green/white/red fascia visible in reporting after the 26 January 2025 relocation. It contains only a pale face/rim, a shallow estimated return, an approximate JR identification mark, the readable Japanese station name, and the dated entrance-only strip. The doorway, passage, jambs, stairs, centre pier, adjacent exit-only sign, policebox and world placement are not modeled. October 2026 presence is unverified.

## Deliverables
- `model/jr_hachiko_entrance_fascia_2025_v001.glb`: isolated runtime-format candidate, not installed in any runtime.
- `model/jr_hachiko_entrance_fascia_2025_v001.blend`: editable component scene with packed font and hidden editable text sources.
- `source/build_fascia.py`: self-contained Blender 4.2.3 generator, including a small renamed OFL font subset. It needs no source photograph, network, external font, or non-Blender Python package.
- `evidence/01_front_graphic_layout.png`, `02_oblique_shallow_return.png`, `03_JR_identity_detail.png`: model-only review images, not photographs.
- `validation/`: generation, clean regeneration and GLB reimport results.

Run with exactly Blender 4.2.3:

    blender -b -t 4 --python-exit-code 1 -P source/build_fascia.py -- --out /absolute/path/to/output

Add `--no-renders` for a clean geometry-only rebuild. The source is the authoritative editable specification. The blend retains editable text sources in a hidden collection; they are excluded from GLB and review renders.

## Important limits
All metric dimensions are estimates: 4.800 m wide × 1.120 m high × 0.202 m deep. They establish a working proportion, not a survey. The shallow back is a technical closure, not an observed concealed enclosure. Colour, finish, line spacing, font, JR logo outlines, mounting depth and exact construction are approximate. Text is modeled as essentially flat planar graphics, not asserted raised lettering. Four materials, no photographic textures.

The JR mark was authored as simplified geometry by eye. It is not official logo artwork, nor a claim of exact reproduction or trademark permission. Typography derives from a renamed Noto Sans CJK Bold JP font subset under SIL OFL; see `source/FONT_LICENSE.txt`. Source photograph redistribution permission was not established, and no photograph/crop bytes are included.

Read `SOURCES_AND_UNCERTAINTIES.md`, `COMPARISON_OBSERVATIONS.md`, and `SELECTIVE_IMPORT.md` before considering placement. H-CV-002 remains partial; the full relocated entrance and 2026 continuity remain on hold. No GitHub, running scene, protected asset, pedestrian display, FPS, merge or deployment was touched.

Graphic surfaces have at most 1 mm of technical separation from the pale face to prevent coplanar rendering. This is not a measured construction detail or an assertion of raised letters.
