# Hachiko local scene fit

Normal display loads `lottery.glb`, `enclosure.glb`, `finish.glb`. These are **estimated placements**, not surveyed positions. `?fit=off` restores the preceding visible facilities and paving. Originals are retained for collision and fallback; only their visible roots are switched after all requested GLBs succeed.

`?fit=preview` additionally loads A8, one station louvre patch, one white-beam bay and a short A8 tactile approach. `?fit=preview&fitparts=a8` (or a comma-separated selection of `a8,louvre,fence,tactile`) isolates proposals. Preview objects do not change the existing entrance collision or create interior/underground functions. They are not asserted as accepted site identifications.

Each `web/*.json` records the actual metres, rotation, ground samples, source basis and remaining uncertainty. GLBs already contain world transforms in the existing T.P.15m datum; the loader does not apply them again. The front-only lottery replaces a northern strip of the small OSM facility while preserving its southern part, smoking cabinet and the PLATEAU context behind it. A8 is a partial replacement variant retaining the northern kiosk roof and side remnants. Only the preview switches that variant.

The enclosure adds a visible 4.6m granite side with short returns; hidden back perimeter is not modeled. The local paving reuses **exactly** the existing `plaza-finish` surface positions and elevations, switching its UV/material once. No nonseamless sample is tiled. The white-beam proposal is one inferred bay between existing rail posts, not repeated 0.57m crop geometry. Its posts/section/terminations and the tactile connection remain preview estimates.

## Rebuild

Use the locally verified extracted deliveries as the first argument; do not run their bundled scripts. No network or photo input is used by this fitting script.

```powershell
python assets/street/hachiko-fit/source/make_fan_paving.py
blender -b --python-exit-code 1 -P assets/street/hachiko-fit/source/fit_scene.py -- <verified-extracted-packages> lottery
```

Repeat the last command for `a8`, `louvre`, `enclosure`, `finish`, `fence`, `tactile`. Blender 5.2.2 and existing Python/Pillow/NumPy were used. [Source rights](source/RIGHTS.md) records source terms; the separate rear-tree folder contains its own attribution and supplied provenance.
